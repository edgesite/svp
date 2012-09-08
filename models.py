from django.db import models

class AddedFile(models.Model):
    '''
      THIS MODEL IS NOT CURRENTLY USED
      intended to allow the user add his or her own files to the repository
    '''
    id = models.AutoField(primary_key=True)
    uploader = models.CharField(blank=True, maxlength=255)
    upfile = models.FileField(upload_to="/tmp/uploaded/")
    csv_isolist = models.TextField()
    class Admin:
        pass

class AllowByIP(models.Model):
    '''
      this model lets the administrator allow users only with certain subnets to access
      specific barcode numbers
    '''
    Id = models.AutoField(primary_key=True)
    Barcode = models.CharField(blank=True, maxlength=255)
    Allow_Subnets = models.CharField(blank=True, maxlength=255)
    class Admin:
        pass

class Biblio(models.Model):
    '''
      this model represents the library's own card catalog entry for catalog keys
      each instance stores the catalog key and associated html
    '''
    Id = models.AutoField(primary_key=True)
    Catalog_Key = models.CharField(blank=True, maxlength=255)
    Bib_Entry = models.TextField()
    class Admin:
        pass

class Conversion(models.Model):
    '''
      this model directs static.py in which file types it converts to what
      each instance stores a list of types from and a single extension to which they are converted
    '''
    id = models.AutoField(primary_key=True)
    fromlist = models.CharField(blank=True, maxlength=255)
    toextension = models.CharField(blank=True, maxlength=10)
    async = models.BooleanField()
    class Admin:
        pass

class Iso(models.Model):
    '''
      each Iso is the image of one cd, and this model stores additional metadata about each
    '''
    Id = models.IntegerField()
    Call_No = models.CharField(blank=True, maxlength=255)
    Barcode_No = models.CharField(primary_key=True, blank=True, maxlength=255)
    Title = models.CharField(blank=True, maxlength=255)
    Pub_Year = models.CharField(blank=True, maxlength=255)
    Requirements = models.CharField(blank=True, maxlength=255)
    Title_Control_No = models.CharField(blank=True, maxlength=255)
    Format = models.CharField(blank=True, maxlength=255)
    Shelving_Key = models.CharField(blank=True, maxlength=255)
    Class = models.CharField(blank=True, maxlength=255)
    ISO_created = models.CharField(blank=True, maxlength=150)
    Notes = models.TextField(blank=True)
    Install_Notes = models.TextField(blank=True)
    MD5 = models.TextField(blank=True)
    Sort = models.CharField(blank=True, maxlength=255)
    Catalog_Key = models.CharField(blank=True, maxlength=50)
    class Meta:
        db_table = 'iso'
    class Admin:
        pass

class MaskFile(models.Model):
    '''
      this model allows the administrator to mask or restrict certain files or folders
      this is to be used only when another filter (i.e. one based on extension) will not
      catch the file
    '''
    id = models.IntegerField(primary_key=True)
    barcode_no = models.CharField(blank=True, maxlength=255)
    full_path = models.CharField(blank=True, maxlength=255)
    file_name = models.CharField(blank=True, maxlength=255)
    file_extension = models.CharField(blank=True, maxlength=255)
    isdir_flag = models.BooleanField()
    mask_flag = models.BooleanField()
    restrict_flag = models.BooleanField()
    class Admin:
        pass

class Md5(models.Model):
    '''
      THIS MODEL IS NOT CURRENTLY USED
    '''
    Id = models.IntegerField(primary_key=True)
    Barcode_No = models.CharField(maxlength=150)
    File = models.CharField(maxlength=150)
    MD5 = models.CharField(maxlength=150)
    class Meta:
        db_table = 'MD5'
    class Admin:
        pass

class MetaMod(models.Model):
    '''
      this model allows authorized users to add/edit additional metadata
      associated with a specified barcode
    '''
    id = models.AutoField(primary_key=True)
    date_stamp = models.DateTimeField()
    username = models.CharField(blank=True, maxlength=255)
    new_data = models.TextField()
    iso_num = models.CharField(blank=True, maxlength=255)
    class Admin:
        pass
    class Meta:
        permissions = (
            ('can_add', 'Can Add'),)

class Sudoc(models.Model):
    '''
      THIS MODEL IS NOT CURRENTLY USED
    '''
    id = models.IntegerField(primary_key=True)
    title = models.CharField(blank=True, maxlength=255)
    barcode = models.CharField(blank=True, maxlength=150)
    sudoc = models.CharField(blank=True, maxlength=150)
    catalog_number = models.CharField(blank=True, maxlength=150)
    description = models.TextField(blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    winxp_compatible = models.IntegerField()
    win98_compatible = models.IntegerField()
    win31_compatible = models.IntegerField()
    msdos_compatible = models.IntegerField()
    memory_required = models.CharField(blank=True, maxlength=150)
    processor_required = models.CharField(blank=True, maxlength=150)
    diskspace_required = models.CharField(blank=True, maxlength=150)
    video_required = models.CharField(blank=True, maxlength=150)
    sound_required = models.CharField(blank=True, maxlength=150)
    other_hardware = models.TextField(blank=True)
    cd_installed_software = models.TextField(blank=True)
    external_software = models.TextField(blank=True)
    documentation_book = models.IntegerField()
    documentation_readme = models.IntegerField()
    documentation_other = models.TextField(blank=True)
    ascii_text_files = models.IntegerField()
    word_files = models.IntegerField()
    wordperfect_files = models.IntegerField()
    other_text_files = models.TextField(blank=True)
    excel_files = models.IntegerField()
    lotus123_files = models.IntegerField()
    ascii_data_files = models.IntegerField()
    other_data_files = models.TextField(blank=True)
    gif_files = models.IntegerField()
    jpeg_files = models.IntegerField()
    tiff_files = models.IntegerField()
    freehand_files = models.IntegerField()
    chart_files = models.IntegerField()
    other_graphics_files = models.TextField(blank=True)
    quicktime_files = models.IntegerField()
    avi_files = models.IntegerField()
    mpeg_files = models.IntegerField()
    wav_files = models.IntegerField()
    mp3_files = models.IntegerField()
    other_media_files = models.TextField(blank=True)
    total_files = models.IntegerField(null=True, blank=True)
    file_format_notes = models.TextField(blank=True)
    general_notes = models.TextField(blank=True)
    xp_emulation_notes = models.TextField(blank=True)
    win98_emulation_notes = models.TextField(blank=True)
    urls = models.TextField(blank=True)
    class Meta:
        db_table = 'sudoc'
    class Admin:
        pass

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=240)
    class Meta:
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    message = models.TextField()
    class Meta:
        db_table = 'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=150)
    content_type_id = models.IntegerField(unique=True)
    codename = models.CharField(unique=True, maxlength=255)
    class Meta:
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, maxlength=90)
    first_name = models.CharField(maxlength=90)
    last_name = models.CharField(maxlength=90)
    email = models.CharField(maxlength=225)
    password = models.CharField(maxlength=255)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    group_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_user_user_permissions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField(null=True, blank=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(maxlength=255)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=255)
    app_label = models.CharField(unique=True, maxlength=255)
    model = models.CharField(unique=True, maxlength=255)
    class Meta:
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, maxlength=120)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = 'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(maxlength=255)
    name = models.CharField(maxlength=150)
    class Meta:
        db_table = 'django_site'
