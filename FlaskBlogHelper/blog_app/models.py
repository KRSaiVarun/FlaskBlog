from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings


class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_PUBLISHED, _('Published')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
        help_text=_('Enter a descriptive title for your post')
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Write your post content here')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Author')
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Created Date')
    )
    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )
    published_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Published Date')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name=_('Status')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name=_('URL Slug'),
        help_text=_('A URL-friendly version of the title (auto-generated if blank)')
    )

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['author', 'created_date']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
        # Alternative with slug:
        # return reverse('post-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Auto-set published_date when status changes to published
        if self.status == self.STATUS_PUBLISHED and not self.published_date:
            self.published_date = timezone.now()
        elif self.status == self.STATUS_DRAFT:
            self.published_date = None

        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = self._generate_slug()

        # Update the updated_date
        if self.pk:
            self.updated_date = timezone.now()

        super().save(*args, **kwargs)

    def _generate_slug(self):
        """Generate a unique slug from the title."""
        from django.utils.text import slugify
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    def reading_time(self):
        """Estimate reading time in minutes."""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))

    def clean(self):
        """Additional validation."""
        if self.status == self.STATUS_PUBLISHED and not self.published_date:
            self.published_date = timezone.now()

        if len(self.title.strip()) < 5:
            raise ValidationError({
                'title': _('Title must be at least 5 characters long.')
            })


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Biography'),
        help_text=_('Tell us a bit about yourself')
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Location')
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Birth Date')
    )

    # Using ImageField instead of CharField for better file handling
    profile_image = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default='profile_pics/default_profile.png',
        verbose_name=_('Profile Image'),
        help_text=_('Upload a profile picture')
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date Joined')
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name=_('Administrator'),
        help_text=_('Designates whether this user has admin privileges')
    )

    # Additional useful fields
    website = models.URLField(
        blank=True,
        verbose_name=_('Website')
    )
    twitter_handle = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Twitter Handle')
    )

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Delete old image when new one is uploaded
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.profile_image and old_profile.profile_image != self.profile_image:
                    if os.path.isfile(old_profile.profile_image.path):
                        os.remove(old_profile.profile_image.path)
            except Profile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Resize profile image if it exists
        if self.profile_image and hasattr(self.profile_image, 'path'):
            self._resize_image()

    def _resize_image(self):
        """Resize profile image to optimize storage and loading."""
        try:
            img = Image.open(self.profile_image.path)

            # Resize image if larger than 300x300
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)

                # Save resized image
                img.save(self.profile_image.path, optimize=True, quality=85)
        except (IOError, FileNotFoundError, ValueError):
            # If image processing fails, continue without resizing
            pass

    def get_profile_image_url(self):
        """Return the profile image URL, with fallback to default."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/images/default_profile.png'

    @property
    def age(self):
        """Calculate age from birth date."""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def post_count(self):
        """Return the number of posts by this user."""
        return Post.objects.filter(author=self.user).count()

    @property
    def published_post_count(self):
        """Return the number of published posts by this user."""
        return Post.objects.filter(author=self.user, status=Post.STATUS_PUBLISHED).count()


# Signal to automatically create/update profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile when a User is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure profile exists for existing users
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the user profile when the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
