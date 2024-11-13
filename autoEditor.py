
from tkinter import *
from tkinter import filedialog

root = Tk()
root.withdraw()

filetypes = (
		("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.flv"),
		("All files", "*.*")
	)
INITIAL_VIDEO_FILE_NAME = filedialog.askopenfilename(initialdir = "", filetypes=filetypes)

if INITIAL_VIDEO_FILE_NAME == "":
	quit()

print("IMPORTING MODULES")
import librosa
from moviepy.editor import *
import cv2

FPS = 30

VIDEO_FILE_NAME = "temp/video.mp4"
AUDIO_FILE_NAME = "temp/audio.wav"
OUTPUT_VIDEO_NAME = "output/output.mp4"
OUTPUT_AUDIO_NAME = "output/audio.wav"

START_COLOUR = [8,255,19]
END_COLOUR = [1,0,232]
CLEAR_COLOUR = [243,0,2]
VERIFY_COLOUR = [245,0,234]

INDICATOR_POS = [25,25]
VERIFIER_POS = [75,25]

# Dont let CLIP_BEGINNING_FRAME_BUFFER + CLIP_ENDING_FRAME_BUFFER be greater than CONNECTING_FRAME_THRESHOLD
# SPEAKING SETTINGS
AMPLITUDE_THRESHOLD = 0.02
CONNECTING_FRAME_THRESHOLD = 10
CLIP_BEGINNING_FRAME_BUFFER = 1
CLIP_ENDING_FRAME_BUFFER = 3

MASS_CUT_BEGINNING_THRESHOLD = 5
MASS_CUT_ENDING_THRESHOLD = 5


def getKeyFrames(initialFile):
	cap = cv2.VideoCapture(initialFile)

	keyFrames = []

	i = 0
	status = "none"
	previousStatus = "none"
	while True:
		ret, frame = cap.read()
		
		if ret:
			previousStatus = status
			verifierColour = [frame[VERIFIER_POS[1]][VERIFIER_POS[0]][0], frame[VERIFIER_POS[1]][VERIFIER_POS[0]][1], frame[VERIFIER_POS[1]][VERIFIER_POS[0]][2]]

			if verifierColour == VERIFY_COLOUR:
				indicatorColour = [frame[INDICATOR_POS[1]][INDICATOR_POS[0]][0], frame[INDICATOR_POS[1]][INDICATOR_POS[0]][1], frame[INDICATOR_POS[1]][INDICATOR_POS[0]][2]]
				
				if indicatorColour == START_COLOUR:
					status = "start"
				elif indicatorColour == END_COLOUR:
					status = "end"
				elif indicatorColour == CLEAR_COLOUR:
					status = "clear"
				else:
					status = "none"
			else:
				status = "none"

			if previousStatus == "start" and status == "none":
				keyFrames.append(["start", i-1])
			elif previousStatus == "none" and status == "end":
				keyFrames.append(["end", i])
			elif previousStatus == "none" and status == "clear":
				keyFrames.append(["clear", i])

			i += 1

		else:
			break

	return keyFrames

def pruneKeyFrames(keyFrames):
	keyFrameChunks = []

	currentChunk = [None, None]
	for keyFrame in keyFrames:
		if keyFrame[0] == "start":
			if currentChunk[0] != None and currentChunk[1] != None:
				keyFrameChunks.append(currentChunk)
				currentChunk = [None, None]

			currentChunk[0] = keyFrame[1]

		elif keyFrame[0] == "end":
			currentChunk[1] = keyFrame[1]

		elif keyFrame[0] == "clear":
			currentChunk = [None, None]

	if currentChunk[0] != None and currentChunk[1] != None:
		keyFrameChunks.append(currentChunk)

	return keyFrameChunks

def shrinkKeyChunks(keyFrameChunks):
	modifiedChunks = []

	for keyFrameChunk in keyFrameChunks:
		if keyFrameChunk[1] - keyFrameChunk[0] <= MASS_CUT_BEGINNING_THRESHOLD+MASS_CUT_ENDING_THRESHOLD:
			continue

		modifiedChunk = [keyFrameChunk[0] + MASS_CUT_BEGINNING_THRESHOLD, keyFrameChunk[1] - MASS_CUT_ENDING_THRESHOLD]
		modifiedChunks.append(modifiedChunk)

	return modifiedChunks

def exportAudio(videoFile, audioFile):
	video = VideoFileClip(videoFile)
	video.audio.write_audiofile(audioFile, ffmpeg_params=["-ac", "1"]) 

def maxAudioPerFrame(audioFile):
	audio, sfreq = librosa.load(audioFile)
	totalFrames = int(len(audio)/sfreq*FPS) + 1

	amplitudePerFrame = [-100] * totalFrames

	for i, amplitude in enumerate(audio):
		if abs(amplitude) > amplitudePerFrame[int(i/sfreq*FPS)]:
			amplitudePerFrame[int(i/sfreq*FPS)] = abs(amplitude)

	return amplitudePerFrame

def calculateClipLengths(amplitudePerFrame):
	# find points of intrest
	thresholdAmplitudeFrames = []
	for i, amplitude in enumerate(amplitudePerFrame):
		if amplitude >= AMPLITUDE_THRESHOLD:
			thresholdAmplitudeFrames.append(i)

	# connect points of intrest within frame gap (nested array with connected points)
	frameClusters = []
	currentFrameCluster = []
	for i, frame in enumerate(thresholdAmplitudeFrames):
		if i == 0:
			currentFrameCluster.append(frame)
			continue

		if frame - thresholdAmplitudeFrames[i-1] > CONNECTING_FRAME_THRESHOLD:
			frameClusters.append(currentFrameCluster)
			currentFrameCluster = []

		currentFrameCluster.append(frame)

	frameClusters.append(currentFrameCluster)

	# move frames into groups with start and end frames
	frameGroups = []
	for cluster in frameClusters:

		start = cluster[0]
		end = cluster[-1]

		if start - CLIP_BEGINNING_FRAME_BUFFER >= 0:
			start = start - CLIP_BEGINNING_FRAME_BUFFER
		else:
			start = 0

		if end + CLIP_ENDING_FRAME_BUFFER <= len(amplitudePerFrame)-1:
			end = end + CLIP_ENDING_FRAME_BUFFER
		else:
			end = len(amplitudePerFrame)-1

		clusterRange = [start, end]
		frameGroups.append(clusterRange)

	return frameGroups

def renderEdits(videoFile, frameGroups, outputFile):
	video = VideoFileClip(videoFile)

	subClips = []

	for frameGroup in frameGroups:
		subClip = video.subclip(frameGroup[0]/30, frameGroup[1]/30)
		subClips.append(subClip)

	finalVideo = concatenate_videoclips(subClips)
	finalVideo.write_videofile(outputFile)


print("FINDING KEY FRAMES")
keyFrames = getKeyFrames(INITIAL_VIDEO_FILE_NAME)

print("GENERATING MASS CHUNKS")
keyFrameChunks = pruneKeyFrames(keyFrames)

print("TRIMMING MASS CHUNKS")
modifiedChunks = shrinkKeyChunks(keyFrameChunks)

print("RENDERING MASS CUTS")
renderEdits(INITIAL_VIDEO_FILE_NAME, modifiedChunks, VIDEO_FILE_NAME)

print("ANALYZING AUDIO")
exportAudio(VIDEO_FILE_NAME, AUDIO_FILE_NAME)

print("READING FRAMES")
amplitudePerFrame = maxAudioPerFrame(AUDIO_FILE_NAME)

print("GROUPING FRAMES")
frameGroups = calculateClipLengths(amplitudePerFrame)

print("RENDERING VIDEO")
renderEdits(VIDEO_FILE_NAME, frameGroups, OUTPUT_VIDEO_NAME)

print("EXPORTING FINAL AUDIO")
exportAudio(OUTPUT_VIDEO_NAME, OUTPUT_AUDIO_NAME)
