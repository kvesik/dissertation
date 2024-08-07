import sys

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QApplication,
    QGroupBox,
    QCheckBox,
    QSpacerItem,
    QButtonGroup,
    QRadioButton,
    QFrame
)

from PyQt5.QtCore import (
    QSize
)

class HorizontalLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class MainWindow(QMainWindow):
    # Override class constructor
    def __init__(self):
        # You must call the super class method
        super().__init__()

        # self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Learning parameter combinations for Balto-Finnic vowel patterns")
        central_widget = QWidget(self)
        mainlayout = QHBoxLayout()
        mainlayout_L = QVBoxLayout()
        mainlayout_R = QVBoxLayout()
        
        self.Fspecificitywidget = self.create_Fspecificity_widget()
        mainlayout_L.addWidget(self.Fspecificitywidget)
        
        self.magriwidget = self.create_magri_widget()
        mainlayout_L.addWidget(self.magriwidget)

        self.noisewidget = self.create_noise_widget()
        mainlayout_L.addWidget(self.noisewidget)

        self.plasticitywidget = self.create_plasticity_widget()
        mainlayout_R.addWidget(self.plasticitywidget)

        self.undominatedloserswidget = self.create_undominatedlosers_widget()
        mainlayout_R.addWidget(self.undominatedloserswidget)

        self.gravitywidget = self.create_gravity_widget()
        mainlayout_R.addWidget(self.gravitywidget)

        self.Mgeneralitywidget = self.create_Mgen_widget()
        mainlayout_R.addWidget(self.Mgeneralitywidget)

        mainlayout.addLayout(mainlayout_L)
        mainlayout.addLayout(mainlayout_R)
        central_widget.setLayout(mainlayout)
        self.setCentralWidget(central_widget)

    def create_Fspecificity_widget(self):
        Fspecificitywidget = QGroupBox("Specific over general faithfulness")

        self.apriori_cb = QCheckBox("Use a priori ranking of specific over general faithfulness")
        self.apriori_label = QLabel("Minimum a priori distance between specific and general faith")
        aprioribiaslist = [0, 10, 20, 25, 30, 35, 40]
        self.apriori_combobox = QComboBox()
        self.apriori_combobox.addItems([str(bias) for bias in aprioribiaslist])
        # self.apriori_combobox.setEnabled(False)

        self.expandingbias_cb = QCheckBox("Minumum a priori distance increases during simulation")
        expandingbias_label = QLabel("     (diff = actualdistance - currentmindistance; only when diff > 0)")
        expandingbias_btngrp = QButtonGroup()
        epxandingbias1_rb = QRadioButton("Type 1: min distance increases by diff")
        epxandingbias1_rb.setProperty('type', 1)
        expandingbias_btngrp.addButton(epxandingbias1_rb)
        epxandingbias2_rb = QRadioButton("Type 2: min distance increases by diff / 2")
        epxandingbias2_rb.setProperty('type', 2)
        expandingbias_btngrp.addButton(epxandingbias2_rb)
        epxandingbias3_rb = QRadioButton("Type 3: min distance increases by diff / (learning trial #)")
        epxandingbias3_rb.setProperty('type', 3)
        expandingbias_btngrp.addButton(epxandingbias3_rb)

        self.apriori_cb.toggled.connect(self.apriori_combobox.setEnabled)
        self.apriori_combobox.currentIndexChanged.connect(lambda x: self.apriori_cb.setChecked(True))
        self.expandingbias_cb.toggled.connect(lambda checked: self.enableButtonGroup(expandingbias_btngrp, checked))
        expandingbias_btngrp.buttonToggled.connect(lambda x, y: self.expandingbias_cb.setChecked(True))

        self.favourspecificity_cb = QCheckBox("Favour specificity by promoting only specific faith when both specific and general are eligible")

        Fspec_layout = QVBoxLayout()

        Fspec_layout.addWidget(self.apriori_cb)

        apriori_layout = QHBoxLayout()
        apriori_layout.addWidget(self.apriori_label)
        apriori_layout.addWidget(self.apriori_combobox)
        Fspec_layout.addLayout(apriori_layout)

        expandingbias_layout = QVBoxLayout()
        expandingbias_layout.addWidget(self.expandingbias_cb)
        expandingbias_layout.addWidget(expandingbias_label)
        for rb in [epxandingbias1_rb, epxandingbias2_rb, epxandingbias3_rb]:
            rb_layout = QHBoxLayout()
            rb_layout.addSpacerItem(QSpacerItem(20, 0))
            rb_layout.addWidget(rb)
            expandingbias_layout.addLayout(rb_layout)
        Fspec_layout.addLayout(expandingbias_layout)

        Fspec_layout.addWidget(HorizontalLine())

        Fspec_layout.addWidget(self.favourspecificity_cb)

        Fspecificitywidget.setLayout(Fspec_layout)
        return Fspecificitywidget

    def create_magri_widget(self):
        magriwidget = QGroupBox("Promotion fraction for update rule ('Magri update')")
        magri_cb = QCheckBox("Use a non-unit promotion fraction")
        magridef_label = QLabel("     (d = num demotions, p = num promotions)")

        magri_btngrp = QButtonGroup()
        magri1_rb = QRadioButton("Type 1: original 'calibrated' rules from Magri 2012: d / (1 + p)")
        magri1_rb.setProperty('type', 1)
        magri_btngrp.addButton(magri1_rb)
        magri2_rb = QRadioButton("Type 2: 1 / p")
        magri2_rb.setProperty('type', 2)
        magri_btngrp.addButton(magri2_rb)
        magri3_rb = QRadioButton("Type 3: d / (d + p)")
        magri3_rb.setProperty('type', 3)
        magri_btngrp.addButton(magri3_rb)
        magri4_rb = QRadioButton("Type 4: from Magri & Kager 2015: 1 / (1 + p)")
        magri4_rb.setProperty('type', 4)
        magri_btngrp.addButton(magri4_rb)

        magri_cb.toggled.connect(lambda checked: self.enableButtonGroup(magri_btngrp, checked))
        magri_btngrp.buttonToggled.connect(lambda x, y: magri_cb.setChecked(True))

        magri_layout = QVBoxLayout()

        magri_layout.addWidget(magri_cb)
        magri_layout.addWidget(magridef_label)

        for rb in [magri1_rb, magri2_rb, magri3_rb, magri4_rb]:
            rb_layout = QHBoxLayout()
            rb_layout.addSpacerItem(QSpacerItem(20, 0))
            rb_layout.addWidget(rb)
            magri_layout.addLayout(rb_layout)

        magriwidget.setLayout(magri_layout)
        return magriwidget

    def enableButtonGroup(self, btngrp, enable):
        for btn in btngrp.buttons():
            btn.setEnabled(enable)

    def create_noise_widget(self):
        noisewidget = QGroupBox("Learning noise")
        noiseF_label = QLabel("Learning noise for faithfulness constraints")
        noiseF_list = [2]
        self.noiseF_combobox = QComboBox()
        self.noiseF_combobox.addItems([str(noise) for noise in noiseF_list])
        noiseM_label = QLabel("Learning noise for markedness constraints")
        noiseM_list = [2]
        self.noiseM_combobox = QComboBox()
        self.noiseM_combobox.addItems([str(noise) for noise in noiseM_list])
        
        noise_layout = QVBoxLayout()

        noiseF_layout = QHBoxLayout()
        noiseF_layout.addWidget(noiseF_label)
        noiseF_layout.addWidget(self.noiseF_combobox)
        noise_layout.addLayout(noiseF_layout)
        noiseM_layout = QHBoxLayout()
        noiseM_layout.addWidget(noiseM_label)
        noiseM_layout.addWidget(self.noiseM_combobox)
        noise_layout.addLayout(noiseM_layout)

        noisewidget.setLayout(noise_layout)
        return noisewidget

    def create_plasticity_widget(self):
        plasticitywidget = QGroupBox("Learning plasticity")
        LRF_label = QLabel("Plasticity (learning rate) for faithfulness constraints")
        LRF_list = [[2, 0.2, 0.02, 0.002]]
        self.LRF_combobox = QComboBox()
        self.LRF_combobox.addItems(str(LRseries) for LRseries in LRF_list)
        LRM_label = QLabel("Plasticity (learning rate) for markedness constraints")
        LRM_list = [[2, 0.2, 0.02, 0.002]]
        self.LRM_combobox = QComboBox()
        self.LRM_combobox.addItems(str(LRseries) for LRseries in LRM_list)

        plasticity_layout = QVBoxLayout()

        LRF_layout = QHBoxLayout()
        LRF_layout.addWidget(LRF_label)
        LRF_layout.addWidget(self.LRF_combobox)
        plasticity_layout.addLayout(LRF_layout)
        LRM_layout = QHBoxLayout()
        LRM_layout.addWidget(LRM_label)
        LRM_layout.addWidget(self.LRM_combobox)
        plasticity_layout.addLayout(LRM_layout)

        plasticitywidget.setLayout(plasticity_layout)
        return plasticitywidget

    def create_gravity_widget(self):
        gravitywidget = QGroupBox("TODO")
        # TODO implement
        return gravitywidget

    def create_undominatedlosers_widget(self):
        undominatedloserswidget = QGroupBox("TODO")
        # TODO implement
        return undominatedloserswidget

    def create_Mgen_widget(self):
        Mgeneralitywidget = QGroupBox("TODO")
        # TODO implement
        return Mgeneralitywidget

    # def eventFilter(self, obj, event):
    #
    #     # if event.type() == QEvent.MouseButtonPress: # isinstance(obj, QTreeWidget) and
    #     #     print("mouse press") #, obj.currentItem().text(0))
    #     #     # self.mousepressedintreewidget = True
    #     #     pos = event.pos()
    #     #     print(self.treedisplay.itemAt(pos).text(0))
    #     #     return QObject.eventFilter(self, obj, event)
    #     if event.type() == QEvent.KeyPress:
    #         keyevent = QKeyEvent(event)
    #         print("key", keyevent.key())
    #         return QObject.eventFilter(self, obj, event)
    #     # elif event.type() == QEvent.MouseButtonRelease:
    #     #     print("mouse release")
    #     #     # self.mousepressedintreewidget = False
    #     #     return QObject.eventFilter(self, obj, event)
    #     # else:
    #     #     return QObject.eventFilter(self, obj, event)
    #
    #     return QObject.eventFilter(self, obj, event)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
