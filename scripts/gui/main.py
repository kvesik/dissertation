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


class MainWindow(QMainWindow):
    # Override class constructor
    def __init__(self):
        # You must call the super class method
        super().__init__()

        self.setMinimumSize(QSize(480, 80))  # Set sizes
        self.setWindowTitle("Learning parameter combinations for Balto-Finnic vowel patterns")
        central_widget = QWidget(self)  # Create a central widget
        mainlayout = QVBoxLayout()
        
        self.Fspecificitywidget = self.create_Fspecificity_widget()
        mainlayout.addWidget(self.Fspecificitywidget)
        
        self.magriwidget = self.create_magri_widget()
        mainlayout.addWidget(self.magriwidget)

        self.expandingbiaswidget = self.create_expandingbias_widget()
        mainlayout.addWidget(self.expandingbiaswidget)

        self.noisewidget = self.create_noise_widget()
        mainlayout.addWidget(self.noisewidget)

        self.plasticitywidget = self.create_plasticity_widget()
        mainlayout.addWidget(self.plasticitywidget)

        self.undominatedloserswidget = self.create_undominatedlosers_widget()
        mainlayout.addWidget(self.undominatedloserswidget)

        self.gravitywidget = self.create_gravity_widget()
        mainlayout.addWidget(self.gravitywidget)

        self.Mgeneralitywidget = self.create_Mgen_widget()
        mainlayout.addWidget(self.Mgeneralitywidget)

        # selectionlayout = QVBoxLayout()
        #
        # searchlayout = QHBoxLayout()
        #
        # searchlayout.addWidget(QLabel("Enter tree node", self))  # , 0, 0)
        #
        # self.combobox = TreeSearchComboBox(self)
        # self.combobox.setModel(self.comboproxymodel)
        # # self.combobox.insertItem(0, "")
        # # self.combobox.insertSeparator(-1)
        # self.combobox.setCurrentIndex(-1)
        # self.combobox.adjustSize()
        # self.combobox.setEditable(True)
        # self.combobox.setInsertPolicy(QComboBox.NoInsert)
        # self.combobox.setFocusPolicy(Qt.StrongFocus)
        # self.combobox.setEnabled(True)
        # self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        # self.combobox.completer().setFilterMode(Qt.MatchContains)
        # self.combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        # tct = TreeClickTracker(self)
        # self.combobox.installEventFilter(tct)
        # searchlayout.addWidget(self.combobox)
        #
        # selectionlayout.addLayout(searchlayout)
        #
        # self.pathslistview = MyListView()
        # self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.pathslistview.setModel(self.listproxymodel)
        # self.pathslistview.setMinimumWidth(500)
        # selectionlayout.addWidget(self.pathslistview)
        #
        # mainlayout.addLayout(selectionlayout)
        #
        # self.treedisplay = QTreeView()
        # self.treedisplay.setHeaderHidden(True)
        # self.treedisplay.setModel(self.treemodel)
        # self.treedisplay.setMinimumWidth(500)
        #
        # mainlayout.addWidget(self.treedisplay)

        central_widget.setLayout(mainlayout)
        self.setCentralWidget(central_widget)  # Install the central widget

    def create_Fspecificity_widget(self):
        Fspecificitywidget = QGroupBox("Specific over general faithfulness")

        self.apriori_cb = QCheckBox("Use a priori ranking of specific over general faithfulness")
        self.apriori_label = QLabel("Minimum a priori distance between specific and general faith")
        aprioribiaslist = [0, 10, 20, 25, 30, 35, 40]
        self.apriori_combobox = QComboBox()
        self.apriori_combobox.addItems([str(bias) for bias in aprioribiaslist])
        # self.apriori_combobox.setEnabled(False)

        self.apriori_cb.toggled.connect(self.apriori_combobox.setEnabled)
        self.apriori_combobox.currentIndexChanged.connect(lambda x: self.apriori_cb.setChecked(True))

        self.favourspecificity_cb = QCheckBox("Favour specificity by promoting only specific faith when both specific and general are eligible")

        Fspec_layout = QVBoxLayout()

        Fspec_layout.addWidget(self.apriori_cb)

        apriori_layout = QHBoxLayout()
        apriori_layout.addWidget(self.apriori_label)
        apriori_layout.addWidget(self.apriori_combobox)
        Fspec_layout.addLayout(apriori_layout)

        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.HLine)
        horizontal_line.setFrameShadow(QFrame.Sunken)
        Fspec_layout.addWidget(horizontal_line)

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

    def create_expandingbias_widget(self):
        expandingbiaswidget = QWidget()
        # TODO implement
        return expandingbiaswidget

    def create_noise_widget(self):
        noisewidget = QWidget()
        # TODO implement
        return noisewidget

    def create_plasticity_widget(self):
        plasticitywidget = QWidget()
        # TODO implement
        return plasticitywidget

    def create_gravity_widget(self):
        gravitywidget = QWidget()
        # TODO implement
        return gravitywidget

    def create_undominatedlosers_widget(self):
        undominatedloserswidget = QWidget()
        # TODO implement
        return undominatedloserswidget

    def create_Mgen_widget(self):
        Mgeneralitywidget = QWidget()
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
