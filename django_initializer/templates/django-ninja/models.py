from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string



class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.PROTECT)


class ExpirableToken(models.Model):
    class Meta:
        db_table = 'expirable_token'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.token or self.is_expired:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(40))
    
    def set_expiration(self, days=0, hours=0, minutes=0):
        self.expiration_date = timezone.now() + timezone.timedelta(days=days, hours=hours, minutes=minutes)
        self.save()

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now()
    
