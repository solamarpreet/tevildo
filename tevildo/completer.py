import operator
from functools import reduce
from prompt_toolkit.completion import Completer, Completion
from openai import OpenAI

class OpenAISessionCompleter(Completer):
    def __init__(self):
        self.client = OpenAI()
        self.command_dict = {
            'set': {'model' : self.calculate_models(),
                    'prompt' : None,
                    'temperature' : None,
                    },

            'clear': {'all' : None,
                      'messages' : None,
                      'model' : None,
                      'prompt' : None,
                      'temperature' : None,
                    },
                    
            'reset': {'all' : None,
                      'messages' : None,
                      'model' : None,
                      'prompt' : None,
                      'temperature' : None,
                    },
            'show': {'messages' : None,
                      'model' : None,
                      'prompt' : None,
                      'temperature' : None,
                      'settings' : None,
                    },

            'list': {'models' : None,
                     'settings' : None,
                     },
                     
            'exit': None,
                            }
        
        
    def calculate_models(self):
        """Retrieve and format model information from OpenAI."""
        return {model["id"]: None for model in self.client.models.list().model_dump()["data"]}


    def calculate_completions(self, line, is_word_before):
        current_tokens = line.split()
        word_before_cursor = ''
        key_tokens = []
        if not is_word_before:
            word_before_cursor = current_tokens.pop(-1)
        for i in current_tokens:
            if not i[0] == '-':
                key_tokens.append(i)
        try:
            x = reduce(operator.getitem, key_tokens, self.command_dict)
            return x.keys(), word_before_cursor
        except:
            return [], word_before_cursor


    def get_completions(self, document, complete_event):
        is_word_before_cursor = document._is_word_before_cursor_complete()
        words, word_before_cursor = self.calculate_completions(document.text, is_word_before=is_word_before_cursor)
        for word in words:
            if word.startswith(word_before_cursor):
                yield Completion(word, start_position=-len(word_before_cursor))
    