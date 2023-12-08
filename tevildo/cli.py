import os
import sys
from pathlib import Path
from prompt_toolkit import PromptSession
from openai import OpenAI
from dotenv import load_dotenv
from .completer import OpenAISessionCompleter
from prompt_toolkit.key_binding import KeyBindings


class OpenAIPrompt:
    def __init__(self):
        self.key_bindings = KeyBindings()
        self.setup_key_bindings()
        self.openai_completer = OpenAISessionCompleter()
        self.client = OpenAI()
        self.session = PromptSession(key_bindings=self.key_bindings, completer=self.openai_completer)
        self.current_prompt = os.getenv("DEFAULT_OPENAI_PROMPT")
        self.current_model = os.getenv("DEFAULT_OPENAI_MODEL")
        self.current_temperature = os.getenv("DEFAULT_OPENAI_TEMPERATURE")
        self.message_db = [
            {"role": "system", "content": self.current_prompt},
        ]

    def setup_key_bindings(self):
            """Setup key bindings for the prompt session."""
            @self.key_bindings.add('backspace')
            def handle_backspace(event):
                # Handle backspace press
                event.current_buffer.delete_before_cursor()
                event.current_buffer.start_completion()
            @self.key_bindings.add('delete')
            def handle_delete(event):
                # Handle delete press
                event.current_buffer.delete()
                event.current_buffer.start_completion()


    def update_setting(self, attribute: str, value):
        """Update a specific setting attribute with a new value."""
        setattr(self, attribute, value)

    def available_openai_models(self):
        model_dict = {}
        for i in self.client.models.list().model_dump()["data"]:
            model_dict[i["id"]] = None
        return model_dict

    def list_setting(self, attribute: str):
        """Return a specific setting attribute with a new value."""
        return getattr(self, attribute)

    def openai_chat(self):
        collected_chunks = []
        try:
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=self.message_db,
                temperature=float(self.current_temperature),
                stream=True
            )
            for chunk in response:
                chunk_data = chunk.model_dump()["choices"][0]["delta"]["content"]
                if chunk_data:
                    print(chunk_data, end="")
                    collected_chunks.append(chunk_data)
            self.message_db.append({"role": "assistant", "content": "".join(collected_chunks)})

        except KeyboardInterrupt:
            print ("Request Interrupted.\n")
            return

        except Exception as e:
            print(f"Error during OpenAI chat: {e}")

    def cli(self):
        while True:
            try:
                user_input = self.session.prompt("\nTevildo> ", complete_in_thread=True)
                if user_input in ['exit', 'quit', 'exit()', 'quit()', 'q']:
                    break
                
                elif user_input in ['clear messages', 'clear msgs']:
                    self.update_setting('message_db', [{"role": "system", "content": self.current_prompt}])
                    continue

                elif user_input in ['clear model', 'reset model']:
                    self.update_setting('current_model', os.getenv("DEFAULT_OPENAI_MODEL"))
                    print(f"Model is reset.\nCurrent model: {self.current_model}\n")

                elif user_input in ['clear prompt', 'reset prompt']:
                    self.update_setting('current_prompt', os.getenv("DEFAULT_OPENAI_PROMPT"))
                    print(f"Prompt is reset.\nCurrent prompt: {self.current_prompt}\n")

                elif user_input in ['clear temp', 'reset temp', 'clear temperature', 'reset temperature']:
                    self.update_setting('current_temperature', os.getenv("DEFAULT_OPENAI_TEMPERATURE"))
                    print(f"Temperature is reset.\nCurrent temperature: {self.current_temperature}\n")

                elif user_input in ['clear', 'reset', 'restart', 'reset all', 'clear all']:
                    self.update_setting('current_model', os.getenv("DEFAULT_OPENAI_MODEL"))
                    self.update_setting('current_prompt', os.getenv("DEFAULT_OPENAI_PROMPT"))
                    self.update_setting('current_temperature', os.getenv("DEFAULT_OPENAI_TEMPERATURE"))
                    self.update_setting('message_db', [{"role": "system", "content": self.current_prompt}])
                    print(f"Session is reset.\nCurrent model: {self.current_model}\nCurrent prompt: {self.current_prompt}\nCurrent Temperature: {self.current_temperature}\n\n")
                    continue

                elif user_input in ['list models', 'show models']:
                    for i in self.available_openai_models().keys():
                        print(i)
                    continue

                elif user_input.startswith('set model'):
                    self.update_setting('current_model', user_input[10:])
                    print(f"Model changed to: {self.current_model}")
                    continue

                elif user_input.startswith('set prompt'):
                    self.update_setting('current_prompt', user_input[11:])
                    print(f"Prompt changed to: {self.current_prompt}")
                    continue

                elif user_input.startswith('set temp'):
                    temp = user_input.split(" ")
                    self.update_setting('current_temperature', temp[-1])
                    print(f"Temperature changed to: {self.current_temperature}")
                    continue

                elif user_input.startswith('show model'):
                    print(f'Current Model : {self.list_setting("current_model")}')
                    continue

                elif user_input.startswith('show prompt'):
                    print(f'Current Prompt : {self.list_setting("current_prompt")}')
                    continue

                elif user_input.startswith('show temperature'):
                    print(f'Current Temperature : {self.list_setting("current_temperature")}')
                    continue

                elif user_input.startswith('show messages'):
                    print('Current Message DB :')
                    for i in self.list_setting("message_db"):
                        print(i)
                    continue

                elif user_input in ['show', 'list settings', 'show settings']:
                    print(f'Current Model : {self.list_setting("current_model")}')
                    print(f'Current Prompt : {self.list_setting("current_prompt")}')
                    print(f'Current Temperature : {self.list_setting("current_temperature")}')
                    continue

                self.message_db.append({"role": "user", "content": user_input})
                self.openai_chat()

            except KeyboardInterrupt:
                break

            except EOFError:
                break

def main():
    try:
        load_dotenv(Path("~/.tevildo").expanduser())
    except Exception as e:
        print(f"Error loading environment file: {e}")
        sys.exit(1)

    app = OpenAIPrompt()
    app.cli()

if __name__ == "__main__":
    main()