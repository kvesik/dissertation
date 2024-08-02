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
    QSizePolicy,
    QSpacerItem
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
        mainlayout = QHBoxLayout()
        
        Fspecificitywidget = self.create_Fspecificity_widget()
        mainlayout.addWidget(Fspecificitywidget)
        
        # magriwidget = self.create_magri_widget()
        #
        # expandingbiaswidget = self.create_expandingbias_widget()
        #
        # noisewidget = self.create_noise_widget()
        #
        # plasticitywidget = self.create_plasticity_widget()
        #
        # undominatedloserswidget = self.create_undominatedlosers_widget()
        #
        # gravitywidget = self.create_gravity_widget()
        #
        # Mgeneralitywidget = self.create_Mgen_widget()

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

        apriori_label = QLabel("Minimum a priori distance between specific and general faith")
        aprioribiaslist = [0, 10, 20, 25, 30, 35, 40]
        apriori_combobox = QComboBox()
        apriori_combobox.addItems([str(bias) for bias in aprioribiaslist])
        apriori_combobox.setEnabled(False)
        apriori_cb = QCheckBox("Use a priori ranking of specific over general faithfulness")
        apriori_cb.toggled.connect(apriori_combobox.setEnabled)

        favourspecificity_cb = QCheckBox("Favour specificity by promoting only specific faith when both specific and general are eligible")

        Fspec_layout = QVBoxLayout()

        Fspec_layout.addWidget(apriori_cb)

        apriori_layout = QHBoxLayout()
        apriori_layout.addWidget(apriori_label)
        apriori_layout.addWidget(apriori_combobox)
        Fspec_layout.addLayout(apriori_layout)

        Fspec_layout.addSpacerItem(QSpacerItem(0, 20))
        
        Fspec_layout.addWidget(favourspecificity_cb)

        Fspecificitywidget.setLayout(Fspec_layout)
        return Fspecificitywidget

    def create_magri_widget(self):
        magriwidget = QWidget()
        # TODO implement
        return magriwidget

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
