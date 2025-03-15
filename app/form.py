from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Stuff, Category, Series, ProfileUser


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StuffForm(forms.ModelForm, forms.ImageField):
    class Meta:
        model = Stuff
        fields = ('collection', 'category', 'series', 'title', 'description', 'price', 'stock', 'image')

    def save(self, commit=True):
        funko = super(StuffForm, self).save(commit=False)
        if commit:
            funko.save()
        return funko


class CategoryForm(forms.ModelForm, forms.ImageField):
    class Meta:
        model = Category
        fields = ('title', 'description', 'image')

    def save(self, commit=True):
        category = super(CategoryForm, self).save(commit=False)
        if commit:
            category.save()
        return category


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ('name', 'description', 'guide')

    def save(self, commit=True):
        series = super(SeriesForm, self).save(commit=False)
        if commit:
            series.save()
        return series


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = ProfileUser
        fields = ('avatar', 'bio')
    def save(self, commit=True):
        user_p = super(ProfileUserForm, self).save(commit=False)
        if commit:
            user_p.save()
        return user_p