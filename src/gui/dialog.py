from PyQt5.QtWidgets import QMessageBox, QInputDialog


def show_dialog(title, main_message, detail_message=None, additional_detail=None, on_button_clicked=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(main_message)
    if detail_message is not None:
        msg.setInformativeText(detail_message)
    if additional_detail is not None:
        msg.setDetailedText(additional_detail)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    if on_button_clicked is not None:
        msg.buttonClicked.connect(on_button_clicked)
    retrieval = msg.exec_()
    print ("value of pressed message box button:", retrieval)


def show_input_dialog(context, title, message):
    text, ok = QInputDialog.getText(context, title, message)
    return text, ok
