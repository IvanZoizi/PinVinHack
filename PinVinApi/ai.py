import asyncio
import datetime
import os

import subprocess
import pandas as pd

from pydub import AudioSegment
import speech_recognition as speech_recog
from bot import send_message_document

from gpt import *
from promt import *

async def from_void_to_text(file, name_file):
    recog = speech_recog.Recognizer()

    data = []
    # file_on_disk = './Чек-лист/5 образцовых (хороших) звонков с развития/MToxMDIyNTI3NTo1NTQ6MzMwNDQ1OTQ0.mp3'
    # file_id = 'MToxMDIyNTI3NTo1NTQ6MzMwNDQ1OTQ0'
    print(data)
    print(file, name_file)
    subprocess.call(
        ['./ffmpeg/bin/ffmpeg.exe', '-i', str(file),

         f"{name_file}.wav"])
    await asyncio.sleep(10)
    audio = AudioSegment.from_file(f"{name_file}.wav")
    chunk_length_ms = 20000  # 60 секунд
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    # Сохранение частей
    for i, chunk in enumerate(chunks):
        try:
            chunk.export(f"chunk_{name_file}_{i}.wav", format="wav")
            with speech_recog.AudioFile(f"chunk_{name_file}_{i}.wav") as source:
                audio_content = recog.record(source)
                text = recog.recognize_google(audio_content, language='ru')
                print(text)
            data.append(text)
        except Exception as ex:
            print(ex)
        finally:
            os.remove(f"chunk_{name_file}_{i}.wav")

    text = '\n'.join(data)
    print(text)
    return text

# 100 - 24 = 76
async def get_answer_from_gpt(file, file_name):
    text = await asyncio.create_task(from_void_to_text(file, file_name))
    dialog_text = await asyncio.create_task(gpt_request_from_dialog(dialog_answer, text))
    answer_gpt = await asyncio.create_task(gpt_request(answer_logs, dialog_text))
    print(answer_gpt)
    return answer_gpt

async def analytics(name_lid, file_names):
    # await asyncio.sleep(10) Если не работает разкомментить
    data = []
    for number, file in enumerate(file_names):
        title = file.split('/')[-1].split('.')[0]
        print(title)
        text_dialog = await asyncio.create_task(get_answer_from_gpt(file, title))
        print(text_dialog)
        data.append(f"Аналитика по звонку № {number + 1}\n\n{text_dialog}")
        os.remove(f"{title}.wav")
    print('\n\n'.join(data))
    data_for_excel = []
    for num, text in enumerate(data):
        print(num)
        print(file_names[num])
        phone = file_names[num].split('/')[-1].split('_')[1]
        d = [name_lid, phone]
        for elem in text.split('\n'):
            for word in ['Портрет ситуации:', 'Теплота лида:', 'Ситуация:', 'Потребности:', 'Боли:', 'Возражения:', 'Рекомендации чтобы закрыть сделку:', 'Процент соотношения чек-листа:', 'Критические нарушения:']:
                if word.lower().replace(',', '') in elem.lower().replace(',', ''):
                    d.append(elem.replace(word, '') if elem.replace(word, '') else '')
        print(d)
        if len(d) == 11:
            data_for_excel.append(d)

    print(data_for_excel)

    df = pd.DataFrame(data_for_excel, columns=['Имя', 'Номер телефона', 'Портрет ситуации:', 'Теплота лида', 'Ситуация', 'Потребности', 'Боли', 'Возражения', 'Рекомендации, чтобы закрыть сделку', 'Процент соотношения чек-листа', 'Критические нарушения'])

    df.to_excel(f'./reports/Отчет от {datetime.datetime.now().strftime("%d.%m.%Y")} по {name_lid}.xlsx', index=False)

    await asyncio.create_task(send_message_document(name_lid, f'./reports/Отчет от {datetime.datetime.now().strftime("%d.%m.%Y")} по {name_lid}.xlsx'))

    data = []
    df_all_data = pd.read_excel("./Данные.xlsx")
    for i in df_all_data.values:
        data.append(list(i))

    for i in data_for_excel:
        if i not in data:
            data.append(i)

    df_all_data = pd.DataFrame(data, columns=['Имя', 'Номер телефона', 'Портрет ситуации:', 'Теплота лида', 'Ситуация', 'Потребности', 'Боли', 'Возражения', 'Рекомендации, чтобы закрыть сделку', 'Процент соотношения чек-листа', 'Критические нарушения'])
    df_all_data.to_excel("Данные.xlsx", index=False)

    return f'./reports/Отчет от {datetime.datetime.now().strftime("%d.%m.%Y")} по {name_lid}.xlsx', data



if __name__ == "__main__": # MToxMDIyNTI3NToyNjE6NzA0NzQ0NzI4.mp3
    print(os.getcwd())
    asyncio.run(analytics("Иванов А", ['C:\\Users\\imzak\\PycharmProjects\\HackatonInPit\\PinVinApi/data/12.03.2024/Колобанов_+79809993443.mp3',
                                       'C:\\Users\\imzak\\PycharmProjects\\HackatonInPit\\PinVinApi/data/12.03.2024/2025-03-11__10-58-08.mp3',
                                       'C:\\Users\\imzak\\PycharmProjects\\HackatonInPit\\PinVinApi/data/12.03.2024/2025-03-10 09-03-23 +79143232053.mp3',
                                       'C:\\Users\\imzak\\PycharmProjects\\HackatonInPit\\PinVinApi/data/12.03.2024/2025-03-21 14-51-15 +79113824717.mp3']))

# if __name__ == '__main__': # Плохой 44
#     print(datetime.datetime.now().strftime("%H:%M:%S"))
#     print(analytics("Иванов А", ['./Чек-лист/5 образцовых (хороших) звонков с развития/MToxMDIyNTI3NTo1NTQ6MzMwNDQ1OTQ0.mp3', './Чек-лист/2 плохих звонка с развития/2025-03-11__10-58-08.mp3']))
#     print(datetime.datetime.now().strftime("%H:%M:%S"))
#     # get_answer_from_gpt('./Чек-лист/5 образцовых (хороших) звонков с развития/MToxMDIyNTI3NTo1NTQ6MzMwNDQ1OTQ0.mp3', '1231221121123')


# Хорошие холодные (28 72) (88 12)