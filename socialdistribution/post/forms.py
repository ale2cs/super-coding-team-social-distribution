from django import forms 
from .models import Post, Comment

# contains different forms that the user interacts with
# e.g posts, comments, etc.
class CreatePostForm(forms.ModelForm):

    title = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Title',
                                                                'class': 'form-control',
                                                                }),
                                                                label="",
                                                                )

    description = forms.CharField(required=True, 
                           widget=forms.widgets.Textarea(attrs={'placeholder': 'Enter your text here',
                                                                'class': 'form-control',
                                                                }),
                                                                label="",
                                                                )

    visibility = forms.ChoiceField(required=True, choices=(('public', 'PUBLIC'), ('friends', 'FRIENDS')))

    unlisted = forms.BooleanField(required=False)

    
    class Meta:
        model = Post
        fields = ['title', 'description', 'visibility', 'unlisted']
    
class CreateCommentForm(forms.ModelForm):

    content = forms.CharField(max_length=200, 
                              required=False,
                              widget=forms.Textarea(attrs={'placeholder': 'Enter your comment here',
                                                           'class':'form-control',
                                                           }),
                                                           label="",
                                                           )

    class Meta:
        model = Comment
        fields = ['content']