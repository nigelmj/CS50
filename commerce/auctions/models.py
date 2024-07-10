from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    item_name = models.CharField(max_length=100)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goods")
    description = models.TextField()
    image = models.ImageField(upload_to="listing_images", blank=True, null=True)
    start_bid = models.IntegerField()
    class CategoryChoices(models.TextChoices):
        FSH = "FSH", "Fashion"
        ELC = "ELC", "Electronics"
        HME = "HME", "Home"
        TOY = "TOY", "Toys"
        BOK = "BOK", "Books"
        COL = "COL", "Collectibles"
    category = models.CharField(max_length=3, choices=CategoryChoices.choices, blank=True)
    class ConditionChoices(models.TextChoices):
        BRNEW = "BRN", "Brand New"
        OPBOX = "OPB", "Open Box"
        RENEW = "REN", "Renewed"
    condition = models.CharField(max_length=3, choices=ConditionChoices.choices, default=ConditionChoices.BRNEW)
    bid_exist = models.BooleanField(default=False)
    bid_allowed = models.BooleanField(default=True)

    def __str__(self):
        return f"Item ID: {self.id} | {self.item_name}"

class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    bid_amount = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.bidder}'s bid on Item: {self.item.item_name}| Bid Amount: ${self.bid_amount}"

class WatchList(models.Model):
    item = models.ManyToManyField(Listing, related_name="watchlist")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s WatchList"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    def __str__(self):
        return f"{self.commenter} commented on {self.item}"