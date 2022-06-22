from django import forms

class CommentCreationForm(forms.Form):
    text = forms.CharField(max_length=4000, required=True)
    id = forms.IntegerField()

class GroupTopicCreationForm(forms.Form):
    topic_name = forms.CharField(max_length=100)
    group_id = forms.IntegerField()

class GroupTopicCommentCreationForm(forms.Form):
    text = forms.CharField(max_length=4000)
    group_topic_id = forms.IntegerField()