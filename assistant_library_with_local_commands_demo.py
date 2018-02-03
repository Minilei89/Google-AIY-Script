#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import subprocess
import sys
import time

import RPi.GPIO as gpio
import aiy.assistant.auth_helpers
import aiy.audio
import aiy.voicehat
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(message)s"
)

process = {}


def power_off_pi():
    aiy.audio.say("Powering Off!")
    subprocess.call("sudo shutdown now", shell=True)


def reboot_pi():
    aiy.audio.say("Rebooting!")
    subprocess.call("sudo reboot", shell=True)


def listen_classical():
    '''
    You will want to install vlc to enable radio and other music/video options.
    If you look online, you should be able to find .pls files that will allow you to listen to the radio.
    If there is a specific song or video you want to play, you should be able to do that as well.
    '''
    global process
    if process['radio']:
        process['radio'].kill()
    aiy.audio.say("Playing classical music")
    process['radio'] = subprocess.Popen(["/usr/bin/cvlc", "/home/pi/Music/Radio/KUSCMP96.pls"], shell=False)


def play_game():
    global process
    if process['gamestream']:
        process['gamestream'].kill()
    process['gamestream'] = subprocess.Popen(["/usr/bin/moonlight", "stream", "-app", "Cuphead", "-1080"])


def stop_process(proc):
    global process
    process[proc].kill()


def process_event(assistant, event):
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('read')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said', event.args['text'])
        text = event.args['text'].lower()

        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()

        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()

        elif text == 'play classical music':
            assistant.stop_conversation()
            listen_classical()

        elif text == 'play game':
            assistant.stop_conversation()
            play_game()

        elif text == 'stop classical music':
            assistant.stop_conversation()
            stop_process('radio')
    
        elif text == 'stop gamestream':
            assistant.stop_conversation()
            stop_process('gamestream')

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)
    print("process event")


def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            print("ready")
            process_event(assistant, event)


if __name__ == '__main__':
    main()
