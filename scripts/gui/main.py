import sys

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QLayout,
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

        self.Mgeneralitywidget = self.create_Mgenerality_widget()
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
        expandingbias1_rb = QRadioButton("Type 1: min distance increases by diff")
        expandingbias1_rb.setProperty('type', 1)
        expandingbias_btngrp.addButton(expandingbias1_rb)
        expandingbias2_rb = QRadioButton("Type 2: min distance increases by diff / 2")
        expandingbias2_rb.setProperty('type', 2)
        expandingbias_btngrp.addButton(expandingbias2_rb)
        expandingbias3_rb = QRadioButton("Type 3: min distance increases by diff / (learning trial #)")
        expandingbias3_rb.setProperty('type', 3)
        expandingbias_btngrp.addButton(expandingbias3_rb)

        self.apriori_cb.toggled.connect(self.apriori_combobox.setEnabled)
        self.apriori_combobox.currentIndexChanged.connect(lambda x: self.apriori_cb.setChecked(True))
        self.expandingbias_cb.toggled.connect(lambda checked: self.enableButtonGroup(expandingbias_btngrp, checked))
        expandingbias_btngrp.buttonToggled.connect(lambda x, y: self.expandingbias_cb.setChecked(True))

        self.favourspecificity_cb = QCheckBox("Favour specificity by promoting only spec faith when both spec and gen are eligible")

        Fspec_widgettree = {
            self.apriori_cb: {
                self.get_serial_layout([self.apriori_label, self.apriori_combobox], True): {}
            },
            self.expandingbias_cb: {
                expandingbias1_rb: {},
                expandingbias2_rb: {},
                expandingbias3_rb: {}
            },
            HorizontalLine(): {},
            self.favourspecificity_cb: {}
        }
        Fspec_layout = self.get_nested_layout(Fspec_widgettree)

        Fspecificitywidget.setLayout(Fspec_layout)
        return Fspecificitywidget

    def create_magri_widget(self):
        magriwidget = QGroupBox("Promotion fraction for update rule ('Magri update')")
        self.magri_cb = QCheckBox("Use a non-unit promotion fraction")
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

        self.magri_cb.toggled.connect(lambda checked: self.enableButtonGroup(magri_btngrp, checked))
        magri_btngrp.buttonToggled.connect(lambda x, y: self.magri_cb.setChecked(True))

        magri_widgettree = {
            self.magri_cb: {
                magridef_label: {},
                magri1_rb: {},
                magri2_rb: {},
                magri3_rb: {}
            }
        }
        magri_layout = self.get_nested_layout(magri_widgettree)

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

        noise_widgettree = {
            self.get_serial_layout([noiseF_label, self.noiseF_combobox], True): {},
            self.get_serial_layout([noiseM_label, self.noiseM_combobox], True): {}
        }
        noise_layout = self.get_nested_layout(noise_widgettree)

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

        plasticity_widgettree = {
            self.get_serial_layout([LRF_label, self.LRF_combobox], True): {},
            self.get_serial_layout([LRM_label, self.LRM_combobox], True): {}
        }
        plasticity_layout = self.get_nested_layout(plasticity_widgettree)

        plasticitywidget.setLayout(plasticity_layout)
        return plasticitywidget

    def create_gravity_widget(self):
        gravitywidget = QGroupBox("TODO")
        # TODO implement
        return gravitywidget

    def create_undominatedlosers_widget(self):
        undominatedloserswidget = QGroupBox("Demoting losers")
        self.demoteonlyundominated_cb = QCheckBox("Demote only undominated losers")

        undominatedlosers_layout = QVBoxLayout()
        undominatedlosers_layout.addWidget(self.demoteonlyundominated_cb)

        undominatedloserswidget.setLayout(undominatedlosers_layout)
        return undominatedloserswidget

    def create_Mgenerality_widget(self):
        Mgeneralitywidget = QGroupBox("General over specific markedness")

        self.Mgen_cb = QCheckBox("Distribute initial markedness values according to generality")
        
        self.Mgen_btngrp = QButtonGroup()
        Mgen1_rb = QRadioButton("Type 1: generality (application rate) calculated from input file")
        Mgen1_rb.setProperty('type', 1)
        self.Mgen_btngrp.addButton(Mgen1_rb)
        Mgen2_rb = QRadioButton("Type 2: 5 strata, built greedily top-down (cons w/ B5 or F5, then 4, 3, 2, 1)")
        Mgen2_rb.setProperty('type', 2)
        self.Mgen_btngrp.addButton(Mgen2_rb)
        Mgen3_rb = QRadioButton("Type 3: 3 strata, starting w/ segmental cons, then LD VH, then local VH")
        Mgen3_rb.setProperty('type', 3)
        self.Mgen_btngrp.addButton(Mgen3_rb)
        Mgen4_rb = QRadioButton("Type 4: 5 strata, built greedily bottom-up (cons w/ B1 or F1, then 2, 3, 4, 5)")
        Mgen4_rb.setProperty('type', 4)
        self.Mgen_btngrp.addButton(Mgen4_rb)
        
        Mgen1_lowend_label = QLabel("starting value when application rate is 0 (y-int)")
        Mgen1_lowend_list = [25, 50, 75, 100, 150, 200, 300]
        self.Mgen1_lowend_combobox = QComboBox()
        self.Mgen1_lowend_combobox.addItems([str(yint) for yint in Mgen1_lowend_list])
        
        Mgen1_highend_label = QLabel("starting value when application rate is 1 (slope)")
        Mgen1_highend_list = [25, 50, 75, 100, 150, 200, 300]
        self.Mgen1_highend_combobox = QComboBox()
        self.Mgen1_highend_combobox.addItems([str(slope) for slope in Mgen1_highend_list])

        Mgen2_strata_label = QLabel("strata values")
        Mgen_5strata_list = [[180, 160, 140, 120, 100]]
        self.Mgen2_strata_combobox = QComboBox()
        self.Mgen2_strata_combobox.addItems([str(stratum) for stratum in Mgen_5strata_list])

        Mgen3_strata_label = QLabel("strata values")
        Mgen_3strata_list = [[140, 120, 100]]
        self.Mgen3_strata_combobox = QComboBox()
        self.Mgen3_strata_combobox.addItems([str(stratum) for stratum in Mgen_5strata_list])

        Mgen4_strata_label = QLabel("strata values")
        self.Mgen4_strata_combobox = QComboBox()
        self.Mgen4_strata_combobox.addItems([str(stratum) for stratum in Mgen_5strata_list])

        self.Mgen_cb.toggled.connect(lambda checked: self.check_enable_Mgen_options())
        self.Mgen1_lowend_combobox.currentIndexChanged.connect(lambda x: self.Mgen_cb.setChecked(True))
        self.Mgen1_highend_combobox.currentIndexChanged.connect(lambda x: self.Mgen_cb.setChecked(True))
        self.Mgen_btngrp.buttonToggled.connect(lambda x, y: self.Mgen_cb.setChecked(True))

        Mgen_widgettree = {
            self.Mgen_cb: {
                Mgen1_rb: {
                    self.get_serial_layout([Mgen1_lowend_label, self.Mgen1_lowend_combobox], True): {},
                    self.get_serial_layout([Mgen1_highend_label, self.Mgen1_highend_combobox], True): {}
                },
                Mgen2_rb: {
                    self.get_serial_layout([Mgen2_strata_label, self.Mgen2_strata_combobox], True): {}
                },
                Mgen3_rb: {
                    self.get_serial_layout([Mgen3_strata_label, self.Mgen3_strata_combobox], True): {}
                },
                Mgen4_rb: {
                    self.get_serial_layout([Mgen4_strata_label, self.Mgen4_strata_combobox], True): {}
                }
            }
        }
        Mgen_layout = self.get_nested_layout(Mgen_widgettree)

        Mgeneralitywidget.setLayout(Mgen_layout)
        return Mgeneralitywidget
    
    def check_enable_Mgen_options(self):
        pass  # TODO

    def get_nested_layout(self, tree_dict):
        main_layout = QVBoxLayout()
        for (parentwidget, childtree) in tree_dict.items():
            if isinstance(parentwidget, QWidget):
                main_layout.addWidget(parentwidget)
            elif isinstance(parentwidget, QLayout):
                main_layout.addLayout(parentwidget)
            sub_layout = QHBoxLayout()
            sub_layout.addSpacerItem(QSpacerItem(30, 0))
            sub_layout.addLayout(self.get_nested_layout(childtree))
            main_layout.addLayout(sub_layout)
        return main_layout

    def get_serial_layout(self, widgetslist, horizontal):
        layout = QHBoxLayout() if horizontal else QVBoxLayout()
        for item in widgetslist:
            layout.addWidget(item)
        return layout


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
