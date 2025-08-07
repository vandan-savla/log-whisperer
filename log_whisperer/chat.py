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
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage

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
        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation_history = []
        
        # Load log file content
        self.log_content = self._load_log_file()
        
        # Initialize LLM
        self._initialize_llm()
        
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
            
            # Restore memory from conversation history
            for entry in self.conversation_history:
                if entry['type'] == 'human':
                    self.memory.chat_memory.add_user_message(entry['content'])
                elif entry['type'] == 'ai':
                    self.memory.chat_memory.add_ai_message(entry['content'])
            
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
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt with log content"""
        return f"""You are an expert log analyst. You have been provided with a log file to analyze. 
Your job is to help the user understand the log content, identify issues, patterns, errors, and provide insights.

LOG FILE PATH: {self.log_file_path}

LOG CONTENT:
```
{self.log_content[:10000]}{'...' if len(self.log_content) > 10000 else ''}
```

Instructions:
- Analyze the log content thoroughly
- Provide clear, actionable insights
- Identify errors, warnings, and patterns
- Suggest solutions when possible
- Be concise but comprehensive
- If the user asks follow-up questions, maintain context from previous messages
- Focus on the most relevant information for the user's queries
"""
    
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

Type 'quit', 'exit', or press Ctrl+C to end the session.
"""
        
        self._format_response(welcome_msg)
        
        # Set up prompt history
        history_file = self.config.config_dir / "chat_history"
        history = FileHistory(str(history_file))
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = prompt(
                        "\n[bold green]You:[/bold green] ",
                        history=history,
                        console=console
                    ).strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        break
                    
                    # Add user message to history
                    self._add_to_history('human', user_input)
                    self.memory.chat_memory.add_user_message(user_input)
                    
                    # Prepare the full prompt with system context
                    messages = [
                        HumanMessage(content=self._get_system_prompt()),
                        *self.memory.chat_memory.messages[-10:],  # Keep last 10 messages for context
                    ]
                    
                    # Get AI response
                    console.print("\n[dim]Analyzing...[/dim]")
                    response = self.llm.invoke(messages)
                    
                    # Extract content from response
                    if hasattr(response, 'content'):
                        ai_response = response.content
                    else:
                        ai_response = str(response)
                    
                    # Add AI response to history and memory
                    self._add_to_history('ai', ai_response)
                    self.memory.chat_memory.add_ai_message(ai_response)
                    
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