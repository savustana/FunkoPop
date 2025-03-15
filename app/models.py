from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Filter(models.Manager):
    sorted = True

    def get_first_by_id(self, id_car):
        return self.filter(pk=id_car).first()

    def get_all(self):
        return self.all()

    def filter_price_max(self):
        self.sorted = not self.sorted
        return self.all().order_by('price')

    def filter_price_min(self):
        self.sorted = not self.sorted
        return self.all().order_by('-price')

    def filter_custom_price(self, min_price=0, max_price=1000000):
        self.sorted = not self.sorted
        return self.all().filter(price__gte=min_price, price__lte=max_price)

    def filter_search(self, search):
        if self.filter(description__icontains=search):
            return self.filter(description__icontains=search)
        return self.all()



class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='images/')


class Series(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    guide = models.CharField(max_length=50)



class Stuff(models.Model):
    id = models.IntegerField(primary_key=True)
    collection = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True)
    price = models.FloatField(null=True, blank=True)
    description = models.TextField()
    stock = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='images/')


# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     item = models.ForeignKey(FunkoPop, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     total_price = models.PositiveIntegerField(default=0)


class Wishlist(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Stuff, on_delete=models.CASCADE)


class CollectionUser(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Stuff, on_delete=models.CASCADE)

    def get_items(self):
        return self.item


class ProfileUser(models.Model):
    id = models.IntegerField(primary_key=True)
    avatar = models.ImageField(upload_to='images/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(CollectionUser, on_delete=models.CASCADE, null=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, null=True)




class Review(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Stuff, on_delete=models.CASCADE)
    rate = models.IntegerField(default=1, validators=[
        MinValueValidator(1), MaxValueValidator(5)]),
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    Statuses = {
        "W": "Waiting",
        "P": "Pending",
        "S": "Sent",
        "R": "Received",
    }
    id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=10, choices=Statuses)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Stuff)
    total_price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
