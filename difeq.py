# take FFT over section of file
# average into one FFT per file
# difference to reference
# average of differences

import numpy as np
import soundfile as sf
import fourier
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os
import sys
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def spectrum_from_audio(filename, fft_size=4096, hop=256, start=None, end=None):
	print("reading",filename)
	soundob = sf.SoundFile(filename)
	signal = soundob.read(always_2d=True)[:,0]
	sr = soundob.samplerate
	
	#cut the signal
	if end:
		signal = signal[int(start*sr):int(end*sr)]
		
	#get the magnitude spectrum
	#avoid divide by 0 error in log
	imdata = 20 * np.log10(np.abs(fourier.stft(signal, fft_size, hop, "hann")+.0000001))

	return np.mean(imdata, axis=1), sr

def indent(e, level=0):
	i = "\n" + level*"	"
	if len(e):
		if not e.text or not e.text.strip(): e.text = i + "	"
		if not e.tail or not e.tail.strip(): e.tail = i
		for e in e: indent(e, level+1)
		if not e.tail or not e.tail.strip(): e.tail = i
	else:
		if level and (not e.tail or not e.tail.strip()): e.tail = i
		
def write_eq(file_path, freqs, dB):
		tree=ET.ElementTree()
		equalizationeffect = ET.Element('equalizationeffect')
		curve=ET.SubElement(equalizationeffect, 'curve')
		curve.attrib["name"] = os.path.basename(file_path)[:-4]
		for f,d in zip(freqs,dB):
			point=ET.SubElement(curve, 'point')
			point.attrib["f"] = str(f)
			point.attrib["d"] = str(d)
		tree._setroot(equalizationeffect)
		indent(equalizationeffect)
		tree.write(file_path)
		
def get_eq(file_src, file_ref):
	#get the averaged spectrum for this audio file
	fft_size=16384
	hop=8192
	#todo: set custom times for both, if given
	spectrum_src, sr_src = spectrum_from_audio(file_src, fft_size, hop)
	spectrum_ref, sr_ref = spectrum_from_audio(file_ref, fft_size, hop)

	freqs = fourier.fft_freqs(fft_size, sr_src)
	#resample the ref spectrum to match the source
	if sr_src != sr_ref:
		spectrum_ref = np.interp(freqs, fourier.fft_freqs(fft_size, sr_ref), spectrum_ref)
	return freqs, spectrum_ref-spectrum_src
	

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
	
class Window(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)
		
		self.setWindowTitle('Differential EQ')
		self.src_dir = "C:\\"
		self.ref_dir = "C:\\"
		self.out_dir = "C:\\"
		self.names = []
		self.freqs = []
		self.eqs = []
		self.av = []
		self.freqs_av = []

		# a figure instance to plot on
		self.figure = Figure()
		# create an axis
		self.ax = self.figure.add_subplot(111)

		# this is the Canvas Widget that displays the `figure`
		# it takes the `figure` instance as a parameter to __init__
		self.canvas = FigureCanvas(self.figure)

		# this is the Navigation widget
		# it takes the Canvas widget and a parent
		self.toolbar = NavigationToolbar(self.canvas, self)

		# Just some button connected to `plot` method
		self.b_add = QtWidgets.QPushButton('+')
		self.b_add.clicked.connect(self.add)
		self.b_delete = QtWidgets.QPushButton('-')
		self.b_delete.clicked.connect(self.delete)
		self.b_save = QtWidgets.QPushButton('=')
		self.b_save.clicked.connect(self.write)
		self.sp_a = QtWidgets.QSpinBox()
		self.sp_a.valueChanged.connect(self.plot)
		self.sp_a.setRange(0, 22000)
		self.sp_a.setSingleStep(1000)
		self.sp_a.setValue(21000)
		self.sp_b = QtWidgets.QSpinBox()
		self.sp_b.valueChanged.connect(self.plot)
		self.sp_b.setRange(0, 22000)
		self.sp_b.setSingleStep(1000)
		self.sp_b.setValue(22000)

		self.listWidget = QtWidgets.QListWidget()
		
		self.qgrid = QtWidgets.QGridLayout()
		self.qgrid.setHorizontalSpacing(0)
		self.qgrid.setVerticalSpacing(0)
		self.qgrid.addWidget(self.toolbar, 0, 0, 1, 2)
		self.qgrid.addWidget(self.canvas, 1, 0, 1, 2)
		self.qgrid.addWidget(self.listWidget, 2, 0, 5, 1)
		self.qgrid.addWidget(self.b_add, 2, 1)
		self.qgrid.addWidget(self.b_delete, 3, 1)
		self.qgrid.addWidget(self.b_save, 4, 1)
		self.qgrid.addWidget(self.sp_a, 5, 1)
		self.qgrid.addWidget(self.sp_b, 6, 1)
		
		self.setLayout(self.qgrid)
		
		
	def add(self):
		file_src = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Source', self.src_dir, "Audio files (*.flac *.wav *.mp3)")[0]
		if file_src:
			self.src_dir, src_name = os.path.split(file_src)
			file_ref = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Reference', self.ref_dir, "Audio files (*.flac *.wav *.mp3)")[0]
			if file_ref:
				self.ref_dir, ref_name = os.path.split(file_ref)
				eq_name = src_name + " -> " + ref_name
				self.listWidget.addItem(eq_name)
				self.freqs, eq = get_eq(file_src, file_ref)
				self.names.append(eq_name)
				self.eqs.append( eq )
				self.plot()

		
	def delete(self):
		for item in self.listWidget.selectedItems():
			print(item.text())
			for i in reversed(range(0, len(self.names))):
				if self.names[i] == item.text():
					self.names.pop(i)
					self.eqs.pop(i)
			self.listWidget.takeItem(self.listWidget.row(item))
		self.plot()
		
	def write(self):
		file_out = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Average EQ', self.out_dir, "XML files (*.xml)")[0]
		if file_out:
			self.out_dir, eq_name = os.path.split(file_out)
			write_eq(file_out, self.freqs_av, self.av)
		
	def plot(self):

		# discards the old graph
		self.ax.clear()
		if self.names:
			#take the average curve of all differential EQs
			self.av = np.mean(np.asarray(self.eqs), axis=0)
			
			freqs_spaced = np.power(2, np.linspace(0, np.log2(self.freqs[-1]), num=2000))
			#self.av = moving_average(self.av, n=20)
			self.av = np.interp(freqs_spaced, self.freqs, self.av)
			
			n = 50
			#smoothen the curves, and reduce the points with step indexing
			self.freqs_av = moving_average(freqs_spaced, n=n)[::n//3]
			self.av = moving_average(self.av, n=n)[::n//3]
			
			a = self.sp_a.value()
			b = self.sp_b.value()
			#get the gain of the filtered  EQ
			if b:
				upper = self.sp_b.value()
				idx1 = (np.abs(self.freqs_av-70)).argmin()
				idx2 = (np.abs(self.freqs_av-upper)).argmin()
				gain = np.mean(self.av[idx1:idx2])
			else:
				gain = np.mean(self.av)
			self.av -= gain
			
			#fade out?
			if a and b:
				self.av *= np.interp(self.freqs_av, (a, b), (1, 0) )
				
			#take the average
			self.ax.semilogx(self.freqs_av, self.av, basex=2, linewidth=2.5)
			
			#plot the contributing raw curves
			for name, eq in zip(self.names, self.eqs):
				self.ax.semilogx(self.freqs, eq, basex=2, linestyle="dashed", linewidth=.5)
		# refresh canvas
		self.canvas.draw()

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)

	main = Window()
	main.show()

	sys.exit(app.exec_())