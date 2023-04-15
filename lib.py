import json
import os
import shutil
import openai


def get_settings_from_config(conf_file_path='config.json'):
    with open(conf_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        # Get the value of a specific key
        api_key = config['openai']['key']
        system_content = config['openai']['system_content']
        model = config['openai']['model']
    return api_key, system_content, model


def transcribe(audio_file_path):
    output_filename = 'out.wav'
    tmp_dir = os.path.dirname(audio_file_path)
    file_path_for_whisper = os.path.join(tmp_dir, output_filename)
    shutil.copyfile(audio_file_path, file_path_for_whisper)

    audio = open(file_path_for_whisper, 'rb')
    transcript = openai.Audio.transcribe('whisper-1', audio)
    return transcript['text']


class Advisor():
    def __init__(self, api_key: str, system_content: str,
                 model: str = 'gpt-3.5-turbo',
                 max_token_num: int = 3000) -> None:
        openai.api_key = api_key
        self.msg = [{'role': 'system', 'content': system_content}]
        self.model = model
        self.max_token_num = max_token_num

    def advise(self, prompt: str) -> str:
        self.msg.append({'role': 'user', 'content': prompt})
        res = openai.ChatCompletion.create(model=self.model,
                                           messages=self.msg,
                                           temperature=0)
        ans = res['choices'][0]['message']['content'].strip()
        self.msg.append({'role': 'assistant', 'content': ans})
        if res['usage']['total_tokens'] > self.max_token_num:
            self.msg.pop(1)
        return ans


def _main(prompt: str, conf_file_path='config.json'):
    api_key, system_content, model = get_settings_from_config(conf_file_path)
    advisor = Advisor(api_key, system_content, model=model)
    ans = advisor.advise(prompt)
    print(ans)


if __name__ == '__main__':
    conf_file_path = 'config_for_test.json'
    model = 'gpt-3.5-turbo'
    prompts = ['御社の「なんでも予測するマン」の中のロジックはただの線形回帰ではないのですか。ディープラーニング系のプロダクトより劣るのでは？',
               'いまいちあなたの言い分は信じられませんね。先程の精度検証のスライドを見ましたが、現在の一般的なプロダクトに比べるとアンダーフィッティング過ぎます。']

    # conf_file_path = 'config_for_test_cynical_commentator.json'
    # prompts = [
    #     '今は「なんでも予測するマン」のように、人間を助けてくれるAIが増えていますね。これからは人間はAIの力を借りてもっと賢くなれるのでしょうか。']
    for prompt in prompts:
        _main(prompt, conf_file_path)
