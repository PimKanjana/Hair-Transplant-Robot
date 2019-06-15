# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\Dialog_after_start.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog2(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(434, 169)
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("hairstyle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		Dialog.setWindowIcon(icon)
		self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
		self.buttonBox.setGeometry(QtCore.QRect(70, 120, 341, 32))
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName("buttonBox")
		self.label = QtWidgets.QLabel(Dialog)
		self.label.setGeometry(QtCore.QRect(20, -10, 381, 101))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(11)
		self.label.setFont(font)
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.label.setObjectName("label")
		self.label_2 = QtWidgets.QLabel(Dialog)
		self.label_2.setGeometry(QtCore.QRect(10, 50, 241, 41))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(11)
		self.label_2.setFont(font)
		self.label_2.setAlignment(QtCore.Qt.AlignCenter)
		self.label_2.setObjectName("label_2")

		self.retranslateUi(Dialog)
		self.buttonBox.accepted.connect(Dialog.accept)
		self.buttonBox.rejected.connect(Dialog.reject)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "FUE Start (warning!)"))
		self.label.setText(_translate("Dialog", "Please make sure that you and your patient "))
		self.label_2.setText(_translate("Dialog", "are in the right position!"))


if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	Dialog = QtWidgets.QDialog()
	ui = Ui_Dialog2()
	ui.setupUi(Dialog)
	Dialog.show()
	sys.exit(app.exec_())

