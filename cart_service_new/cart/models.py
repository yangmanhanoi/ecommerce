from django.db import models


from bson import ObjectId

class Cart(models.Model):
    user_id = models.CharField(max_length=50) # Reference to Customer in MySQL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=50)  # Reference to Product in MongoDB
    quantity = models.IntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    def set_product_id(self, obj_id):
        """Ensure ObjectId is stored as a string"""
        if isinstance(obj_id, ObjectId):
            self.product_id = str(obj_id)
        else:
            self.product_id = obj_id