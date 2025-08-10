"""
Chat interface with memory persistence for log analysis
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from langchain.schema import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import hashlib

from .config import Config
from .llm_factory import llm_factory

console = Console()


class LogAnalyzer:
    """Main chat interface for log analysis"""
    
    def __init__(self, log_file_path: str, save_path: Optional[str] = None):
        self.log_file_path = Path(log_file_path)
        self.save_path = Path(save_path) if save_path else None
        self.config = Config()
        self.llm = None
        self.conversation_history = []
        self.retriever = None
        self.rag_chain = None
        
        # Load log file content
        self.log_content = self._load_log_file()
        
        # Initialize LLM
        self._initialize_llm()
        
        # RAG chain will be initialized lazily on first use to speed startup
        
        # Load previous conversation if save path exists
        if self.save_path and self.save_path.exists():
            self._load_conversation()
    
    def _load_log_file(self) -> str:
        """Load and return log file content"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            console.print(f"[green]✓ Loaded log file: {self.log_file_path}[/green]")
            console.print(f"[dim]Log file size: {len(content)} characters[/dim]")
            return content
        except Exception as e:
            console.print(f"[red]✗ Failed to load log file: {e}[/red]")
            raise
    
    def _initialize_llm(self):
        """Initialize the LLM from configuration"""
        provider_config = self.config.get_provider_config()
        if not provider_config:
            raise ValueError("No LLM provider configured. Please run 'log-whisperer configure' first.")
        
        try:
            self.llm = llm_factory.create_llm(
                provider_config["provider"],
                provider_config["model"],
                provider_config
            )
            console.print(f"[green]✓ Initialized {provider_config['provider']} with model {provider_config['model']}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize LLM: {e}[/red]")
            raise
    
    def _load_conversation(self):
        """Load previous conversation from save file"""
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.conversation_history = data.get('conversation', [])
            
            # Memory is derived on the fly from conversation_history; nothing else to do here
            
            console.print(f"[green]✓ Loaded previous conversation with {len(self.conversation_history)} messages[/green]")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load previous conversation: {e}[/yellow]")
    
    def _save_conversation(self):
        """Save conversation to file"""
        if not self.save_path:
            return
        
        try:
            # Ensure directory exists
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'log_file': str(self.log_file_path),
                'conversation': self.conversation_history
            }
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            console.print(f"[red]Warning: Could not save conversation: {e}[/red]")
    
    def _get_system_instructions(self) -> str:
        """System instructions for the RAG chain (no full log in prompt)."""
        with open("E:/Codes/AI/log-whisperer/log_whisperer/prompts/system_prompt.txt", "r") as f:
            return f.read()
    
    def _index_cache_dir(self) -> Path:
        base = self.config.config_dir / "indexes"
        base.mkdir(parents=True, exist_ok=True)
        # Fingerprint by file path, size, mtime, and chunking/version params
        stat = self.log_file_path.stat()
        finger_str = json.dumps({
            "path": str(self.log_file_path.resolve()),
            "size": stat.st_size,
            "mtime": int(stat.st_mtime),
            "chunk_size": 2000,
            "chunk_overlap": 200,
            "embedding": "fastembed-bge-small-en-v1.5",
            "version": 1,
        }, sort_keys=True)
        digest = hashlib.sha256(finger_str.encode("utf-8")).hexdigest()[:16]
        return base / digest

    def _initialize_rag(self, force_rebuild: bool = False) -> None:
        """Create or load a vector store retriever and retrieval chain over the log file.

        Lazy + cached: load FAISS if available, else build and persist.
        """
        try:
            console.print("[yellow] Retrieving Embeddings...[/yellow]")
            cache_dir = self._index_cache_dir()
            # embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

            if cache_dir.exists() and not force_rebuild:
                vector_store = FAISS.load_local(
                    str(cache_dir), embeddings, allow_dangerous_deserialization=True
                )
            else:
                splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, add_start_index=True)

                documents = splitter.create_documents(
                    [self.log_content], metadatas=[{"source": str(self.log_file_path)}]
                )
                vector_store = FAISS.from_documents(documents, embeddings)
                vector_store.save_local(str(cache_dir))

            self.retriever = vector_store.as_retriever(search_kwargs={"k": 6})

            # Prompt and retrieval chain
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_instructions}\n\nRetrieved context:\n{context}"),
                ("human", "This is user query - {input}. ")
            ])
            document_chain = create_stuff_documents_chain(self.llm, prompt)
            self.rag_chain = create_retrieval_chain(self.retriever, document_chain)
            console.print("[green]✓ Log are retrieved and ready to be analyzed[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to initialize Log retriever: {e}[/yellow]")
            self.retriever = None
            self.rag_chain = None
    
    def _format_response(self, response: str) -> None:
        """Format and display AI response"""
        panel = Panel(
            Markdown(response),
            title="[bold blue]Agent[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(panel)
    
    def _add_to_history(self, message_type: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def start_chat(self):
        """Start the interactive chat session"""
        # Welcome message
        welcome_msg = f"""🔍 **Welcome to Log Whisperer!**

            I'm ready to help you analyze your log file: `{self.log_file_path.name}`

            You can ask me questions like:
            - "What errors do you see in this log?"
            - "Summarize the main events"
            - "Are there any patterns or anomalies?"
            - "What happened around timestamp X?"

            Type '/quit', '/exit', or press Ctrl+C to end the session.
        """
        self._initialize_rag()
        
        self._format_response(welcome_msg)
        
        # Set up prompt history
        history_file = self.config.config_dir / "chat_history"
        history = FileHistory(str(history_file))
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = prompt(
                        "You: ",
                        history=history
                    ).strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['/quit', '/exit']:
                        break
                    
                    # Add user message to history
                    self._add_to_history('human', user_input)
                    
                    # Get AI response (RAG if available; fallback to direct LLM)
                    console.print("\n[dim]Analyzing...[/dim]")
                    # if self.rag_chain is None:
                    #     self._initialize_rag()

                    if self.rag_chain is not None:
                        result = self.rag_chain.invoke({
                            "input": user_input,
                            "system_instructions": self._get_system_instructions(),
                        })
                        ai_response = result.get("answer") or str(result)
                    else:
                        # Fallback: direct invocation with minimal context
                        recent_messages: List[BaseMessage] = []
                        for entry in self.conversation_history[-10:]:
                            if entry['type'] == 'human':
                                recent_messages.append(HumanMessage(content=entry['content']))
                            elif entry['type'] == 'ai':
                                recent_messages.append(AIMessage(content=entry['content']))
                        messages = [HumanMessage(content=self._get_system_instructions()), *recent_messages, HumanMessage(content=user_input)]
                        response = self.llm.invoke(messages)
                        ai_response = response.content if hasattr(response, "content") else str(response)
                    
                    # Add AI response to history
                    self._add_to_history('ai', ai_response)
                    
                    # Display response
                    self._format_response(ai_response)
                    
                    # Save conversation
                    self._save_conversation()
                    
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    console.print(f"\n[red]Error: {e}[/red]")
                    continue
        
        finally:
            console.print("\n[yellow]Goodbye! Your conversation has been saved.[/yellow]")
            self._save_conversation()
