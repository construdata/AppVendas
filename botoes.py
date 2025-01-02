from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior

class ImageButton(ButtonBehavior, Image):#ButtonBehavior precisa ser o 1º
    pass

class LabelButton(ButtonBehavior, Label): #ButtonBehavior precisa ser o 1º
    pass