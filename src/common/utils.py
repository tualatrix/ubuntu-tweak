def set_label_for_stock_button(button, text):
    label = button.get_child().get_child().get_children()[1]
    label.set_text(text)
