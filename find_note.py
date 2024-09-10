import copy
import numpy as np
import scipy.fftpack
import sounddevice as sd
import time
import threading
class FindNote():
    def __init__(self):
        self.SAMPLE_FREQ = 44100
        self.WINDOW_SIZE = 44100
        self.WINDOW_STEP = 12000
        self.NUM_HPS = 5
        self.POWER_THRESH = 1e-6
        self.CONCERT_PITCH = 440
        self.WHITE_NOISE_THRESH = 0.2
        self.WINDOW_T_LEN = self.WINDOW_SIZE / self.SAMPLE_FREQ
        self.SAMPLE_T_LENGTH = 1 / self.SAMPLE_FREQ
        self.DELTA_FREQ = self.SAMPLE_FREQ / self.WINDOW_SIZE
        self.OCTAVE_BANDS = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]
        self.ALL_NOTES = ["Ля", "Ля#", "Си", "До", "До#", "Ре", "Ре#", "Ми", "Фа", "Фа#", "Соль", "Соль#"]
        self.HANN_WINDOW = np.hanning(self.WINDOW_SIZE)
        self.is_listening = True
        self.found_notes = []
        self.num_note = 0
        self.step_note = 0
        self.pred_note = ''
        self.note_for_render = ''

        self.notes_to_semitones = {
            'До': 8, 'До#': 9, 'Ре': 10, 'Ре#': 11, 'Ми': 0, 'Фа': 1,
            'Фа#': 2, 'Соль': 3, 'Соль#': 4, 'Ля': 5, 'Ля#': 6, 'Си': 7
        }
        self.strings = {
            'Ми': 1, 'Си': 2, 'Соль': 3, 'Ре': 4, 'Ля': 5
        }

    def calculate_fret(self, note, octave):
        fNote = self.notes_to_semitones[note]
        if fNote <= 4 and octave == 2:
            string = 1
            return fNote, string
        elif (fNote >= 5 and fNote  <= 7 and octave == 2) or (fNote >= 8 and fNote <= 9 and octave == 3):
            fNote -= 5
            string = 2
            return fNote, string
        elif (fNote >= 10 and fNote <= 11 and octave == 3):
            fNote -= 10
            string = 3
            return fNote, string
        elif (fNote <= 2 and octave == 3):
            fNote += 2
            string = 3
            return fNote, string
        elif fNote >= 3 and fNote <= 6 and octave == 3:
            fNote -= 3
            string = 4
            return fNote, string
        elif fNote == 7 and octave == 3:
            fNote = 0
            string = 5
            return fNote, string
        elif (fNote >= 8 and fNote <= 11 and octave == 4):
            fNote -= 7
            string = 5
            return fNote, string
        else:
            string = 6
        return fNote, string

    def find_closest_note(self, pitch):
        i = int(np.round(np.log2(pitch / self.CONCERT_PITCH) * 12))
        closest_note = self.ALL_NOTES[i % 12] + " " + str(4 + (i + 9) // 12)
        closest_pitch = self.CONCERT_PITCH * 2 ** (i / 12)
        return closest_note, closest_pitch

    def callback(self, indata, frames, time, status):
        if not hasattr(self.callback, "window_samples"):
            FindNote.callback.window_samples = [0 for _ in range(self.WINDOW_SIZE)]
        if not hasattr(self.callback, "noteBuffer"):
            FindNote.callback.noteBuffer = ["1", "2"]

        if status:
            print(status)
            return
        if any(indata):
            FindNote.callback.window_samples = np.concatenate((FindNote.callback.window_samples, indata[:, 0]))
            FindNote.callback.window_samples = FindNote.callback.window_samples[len(indata[:, 0]):]

            signal_power = (np.linalg.norm(self.callback.window_samples, ord=2) ** 2) / len(self.callback.window_samples)
            if signal_power < self.POWER_THRESH:
                #os.system('cls' if os.name == 'nt' else 'clear')
                #print("Closest note: ...")
                return

            hann_samples = self.callback.window_samples * self.HANN_WINDOW
            magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[:len(hann_samples) // 2])

            for i in range(int(62 / self.DELTA_FREQ)):
                magnitude_spec[i] = 0

            for j in range(len(self.OCTAVE_BANDS) - 1):
                ind_start = int(self.OCTAVE_BANDS[j] / self.DELTA_FREQ)
                ind_end = int(self.OCTAVE_BANDS[j + 1] / self.DELTA_FREQ)
                ind_end = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
                avg_energy_per_freq = (np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2) / (
                            ind_end - ind_start)
                avg_energy_per_freq = avg_energy_per_freq ** 0.5
                for i in range(ind_start, ind_end):
                    magnitude_spec[i] = magnitude_spec[i] if magnitude_spec[
                    i] > self.WHITE_NOISE_THRESH * avg_energy_per_freq else 0

            mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1 / self.NUM_HPS), np.arange(0, len(magnitude_spec)),
                                      magnitude_spec)
            mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)

            hps_spec = copy.deepcopy(mag_spec_ipol)

            for i in range(self.NUM_HPS):
                tmp_hps_spec = np.multiply(hps_spec[:int(np.ceil(len(mag_spec_ipol) / (i + 1)))],
                                           mag_spec_ipol[::(i + 1)])
                if not any(tmp_hps_spec):
                    break
                hps_spec = tmp_hps_spec

            max_ind = np.argmax(hps_spec)
            max_freq = max_ind * (self.SAMPLE_FREQ / self.WINDOW_SIZE) / self.NUM_HPS

            closest_note, closest_pitch = self.find_closest_note(max_freq)
            max_freq = round(max_freq, 1)
            closest_pitch = round(closest_pitch, 1)

            self.callback.noteBuffer.insert(0, closest_note)
            self.callback.noteBuffer.pop()

            #os.system('cls' if os.name == 'nt' else 'clear')
            if self.callback.noteBuffer.count(self.callback.noteBuffer[0]) == len(self.callback.noteBuffer):
                if self.num_note == 0:
                    self.found_notes.append(closest_note)
                    self.num_note += 1
                else:
                    if self.found_notes[self.num_note - 1] != closest_note:
                        self.found_notes.append(closest_note)
                        self.num_note += 1
                        self.step_note += 15



        else:
            print('no input')

    def search_last_note_periodically(self, interval):
        while self.is_listening:
            if self.found_notes:
                self.note_for_render = self.found_notes[-1]
                if len(self.found_notes) > 1:
                    self.pred_note = self.found_notes[-2]
            time.sleep(interval)

    def start_listening(self):
        self.search_for_render = threading.Thread(target=self.search_last_note_periodically, args=(0.1,))
        self.search_for_render.start()
        try:
            with sd.InputStream(channels=1, callback=self.callback, blocksize=self.WINDOW_STEP, samplerate=self.SAMPLE_FREQ):
                while self.is_listening:
                    time.sleep(0.1)

        except Exception as exc:
            print(str(exc))