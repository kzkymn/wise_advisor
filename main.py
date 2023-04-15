import argparse
import os
import gradio as gr

from lib import Advisor, get_settings_from_config, transcribe


def get_q_and_a(audio_file_path, advisor):
    chat_history_list = []
    if len(advisor.msg_list) > 1:
        i = 1
        while i < len(advisor.msg_list):
            chat_history_list.append(
                (advisor.msg_list[i]['content'], advisor.msg_list[i+1]['content']))
            i += 2

    question_txt = transcribe(audio_file_path)
    answer_txt = advisor.advise(question_txt)
    chat_history_list.append((question_txt, answer_txt))
    # q_and_a_txt = 'Q:\n' + question_txt + '\n\nA:\n' + answer_txt
    # return q_and_a_txt, advisor

    return chat_history_list, advisor


def create_gradio_interface(api_key, system_content, model):
    advisor_state = gr.State(Advisor(api_key, system_content, model=model))
    chatbot = gr.Chatbot()
    return gr.Interface(
        fn=get_q_and_a,
        inputs=[gr.Audio(source='microphone', type='filepath'), advisor_state],
        # outputs=['text', advisor_state],
        outputs=[chatbot, advisor_state],
        examples=['audio/sample_audio.wav', 'audio/sample_audio_2.wav'],
        allow_flagging='never')


def main(conf_file_path='config.json'):
    api_key, system_content, model = get_settings_from_config(conf_file_path)
    create_gradio_interface(api_key, system_content, model).launch()


if __name__ == '__main__':
    additional_path = os.path.join(os.path.curdir, 'bin')
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + additional_path
    parser = argparse.ArgumentParser(
        description='main logic of Wise Respondent')
    parser.add_argument('--conf', default='config.json',
                        help='path of config file')

    args = parser.parse_args()
    main(conf_file_path=args.conf)
