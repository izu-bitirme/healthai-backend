from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# Ana döngü modeli: hastanın iyileşme süreci
class RecoveryCycle(models.Model):
    CYCLE_TYPES = [
        ("limb_lengthening", "Uzuv Uzatma"),
        ("fracture", "Kırık İyileşme"),
        ("post_surgery", "Ameliyat Sonrası"),
        ("general", "Genel Rehabilitasyon"),
    ]

    patient = models.ForeignKey(
        "user_profile.Patient", on_delete=models.CASCADE, related_name="recovery_cycles"
    )
    cycle_type = models.CharField(
        max_length=20,
        choices=CYCLE_TYPES,
        default="general",
        blank=True,
        help_text="Rehabilitasyon tipi",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    goal_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True, editable=True, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.profile.user.username} - {self.get_cycle_type_display()} ({self.start_date} - {self.end_date})"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Bitiş tarihi başlangıç tarihinden önce olamaz")
        super().save(*args, **kwargs)


# Günlük log: her günün durumu
class DailyRecoveryLog(models.Model):
    recovery_cycle = models.ForeignKey(
        "RecoveryCycle", on_delete=models.CASCADE, related_name="daily_logs"
    )
    date = models.DateField(default=timezone.now)

    # Fiziksel
    pain_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="0(ağrı yok) - 10(kullanılamaz)",
    )
    mobility_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="0(hareketsiz) - 10(tam hareket)",
    )
    swelling_present = models.BooleanField(null=True, blank=True)
    fever = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(35), MaxValueValidator(42)],
    )

    # Mental
    mood_level = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    appetite_level = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    # Genel notlar
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recovery_cycle.patient.profile.user.username} - Log {self.date}"

    @property
    def overall_score(self):
        vals = [
            self.pain_level if self.pain_level is not None else 5,
            self.mobility_score if self.mobility_score is not None else 5,
            self.mood_level if self.mood_level is not None else 5,
        ]
        return sum(vals) / len(vals)


# Egzersiz kayıtları
class ExerciseLog(models.Model):
    EXERCISE_TYPES = [
        ("stretching", "Esneme"),
        ("strength", "Kuvvet"),
        ("cardio", "Kardiyo"),
        ("balance", "Denge"),
        ("functional", "Fonksiyonel"),
    ]
    INTENSITY_CHOICES = [(i, str(i)) for i in range(1, 6)]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="exercises"
    )
    exercise_name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField(
        help_text="Süre (dk)", validators=[MinValueValidator(1), MaxValueValidator(300)]
    )
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPES)
    intensity = models.PositiveSmallIntegerField(choices=INTENSITY_CHOICES, default=3)
    sets = models.PositiveSmallIntegerField(null=True, blank=True, default=1)
    reps = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=True)
    pain_during_exercise = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.exercise_name} ({self.duration_minutes} dk)"


# İlaç kayıtları
class MedicationLog(models.Model):
    FREQUENCY_CHOICES = [
        ("once", "Günde 1"),
        ("twice", "Günde 2"),
        ("thrice", "Günde 3"),
        ("as_needed", "İhtiyaç halinde"),
    ]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="medications"
    )
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, default="once", blank=True, null=True
    )
    taken = models.BooleanField(default=False)
    time_taken = models.TimeField(null=True, blank=True)
    side_effects = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"


# Beslenme kayıtları
class NutritionLog(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Kahvaltı"),
        ("lunch", "Öğle"),
        ("dinner", "Akşam"),
        ("snack", "Ara"),
    ]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="nutrition"
    )
    meal_type = models.CharField(
        max_length=20, choices=MEAL_CHOICES, default="breakfast"
    )
    calories = models.PositiveIntegerField()
    protein_g = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    carbs_g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    water_intake_ml = models.PositiveIntegerField(null=True, blank=True)
    supplements = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.calories} kcal"


# Uyku kayıtları
class SleepLog(models.Model):
    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="sleep"
    )
    sleep_duration = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.5), MaxValueValidator(24)],
    )
    sleep_quality = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    bedtime = models.TimeField(null=True, blank=True, default="23:59")
    wakeup_time = models.TimeField(null=True, blank=True)
    naps_duration = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Gündüz uykusu (saat)",
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sleep_duration} saat"


# Ağrı detay logu
class PainLog(models.Model):
    BODY_PARTS = [
        ("head", "Baş"),
        ("neck", "Boyun"),
        ("shoulder", "Omuz"),
        ("arm", "Kol"),
        ("elbow", "Dirsek"),
        ("wrist", "Bilek"),
        ("hand", "El"),
        ("chest", "Göğüs"),
        ("back", "Sırt"),
        ("lower_back", "Bel"),
        ("hip", "Kalça"),
        ("thigh", "Uyluk"),
        ("knee", "Diz"),
        ("calf", "Baldır"),
        ("ankle", "Ayak Bileği"),
        ("foot", "Ayak"),
    ]
    PAIN_TYPES = [
        ("sharp", "Keskin"),
        ("dull", "Donuk"),
        ("throbbing", "Zonklayıcı"),
        ("burning", "Yanıcı"),
        ("stabbing", "Bıçak"),
    ]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="pain_details"
    )
    body_part = models.CharField(max_length=20, choices=BODY_PARTS)
    intensity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    pain_type = models.CharField(
        max_length=20, choices=PAIN_TYPES, null=True, blank=True, default="sharp"
    )
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    triggered_by = models.CharField(max_length=100, null=True, blank=True)
    relieved_by = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_body_part_display()} - Şiddet: {self.intensity}"


# Ruh hali logu
class MoodLog(models.Model):
    MOOD_TYPES = [
        ("happy", "Mutlu"),
        ("sad", "Üzgün"),
        ("anxious", "Endişeli"),
        ("angry", "Kızgın"),
        ("tired", "Yorgun"),
        ("energetic", "Enerjik"),
        ("neutral", "Nötr"),
    ]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="moods"
    )
    mood_description = models.CharField(max_length=20, choices=MOOD_TYPES)
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    triggers = models.TextField(blank=True, null=True, default="")
    coping_mechanisms = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_mood_description_display()} - Seviye: {self.level}"


# Uzuv uzatma bilgisi
class LimbLengtheningInfo(models.Model):
    BONE_CHOICES = [
        ("femur", "Femur"),
        ("tibia", "Tibia"),
        ("humerus", "Humerus"),
        ("fibula", "Fibula"),
    ]
    DEVICE_TYPES = [
        ("precice", "PRECICE"),
        ("lrs", "LRS"),
        ("ilizarov", "Ilizarov"),
        ("other", "Diğer"),
    ]

    recovery_cycle = models.OneToOneField(
        RecoveryCycle, on_delete=models.CASCADE, related_name="limb_lengthening_info"
    )
    bone = models.CharField(max_length=20, choices=BONE_CHOICES)
    initial_length = models.FloatField(validators=[MinValueValidator(0)])
    target_length = models.FloatField(validators=[MinValueValidator(0)])
    current_length = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    device_model = models.CharField(max_length=100, blank=True, null=True)
    surgery_date = models.DateField()
    surgeon_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recovery_cycle.patient} - {self.get_bone_display()}"

    @property
    def progress_percentage(self):
        if self.current_length is None:
            return 0
        try:
            return (
                (self.current_length - self.initial_length)
                / (self.target_length - self.initial_length)
            ) * 100
        except ZeroDivisionError:
            return 0


# Günlük uzatma miktarı
class DistractionLog(models.Model):
    PIN_SITE_CONDITIONS = [
        ("normal", "Normal"),
        ("redness", "Kızarıklık"),
        ("swelling", "Şişlik"),
        ("discharge", "Akıntı"),
        ("infection", "Enfeksiyon"),
    ]

    daily_log = models.ForeignKey(
        DailyRecoveryLog, on_delete=models.CASCADE, related_name="distraction_logs"
    )
    distraction_amount = models.FloatField(
        validators=[MinValueValidator(0.25), MaxValueValidator(2.0)],
        help_text="Günlük uzatma (mm)",
    )
    total_distraction = models.FloatField(null=True, blank=True)
    pin_site_condition = models.CharField(
        max_length=20, choices=PIN_SITE_CONDITIONS, default="normal"
    )
    pin_site_notes = models.TextField(blank=True, null=True)
    xray_notes = models.TextField(blank=True, null=True)
    adjustment_notes = models.TextField(blank=True, null=True)
    pain_during_distraction = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.daily_log.date} - {self.distraction_amount}mm"

    def save(self, *args, **kwargs):
        if self.total_distraction is None:
            prev = (
                DistractionLog.objects.filter(
                    daily_log__recovery_cycle=self.daily_log.recovery_cycle,
                    daily_log__date__lt=self.daily_log.date,
                )
                .order_by("-daily_log__date")
                .first()
            )
            self.total_distraction = (
                prev.total_distraction if prev else 0
            ) + self.distraction_amount
        super().save(*args, **kwargs)


# Kemik kaynama kontrolleri
class BoneConsolidationCheck(models.Model):
    CALLUS_CHOICES = [
        ("none", "Yok"),
        ("minimal", "Minimal"),
        ("moderate", "Orta"),
        ("good", "İyi"),
        ("excellent", "Mükemmel"),
    ]
    WEIGHT_CHOICES = [
        ("none", "Yasak"),
        ("toe_touch", "Parmak Ucu"),
        ("partial", "Kısmi"),
        ("full", "Tam"),
    ]

    recovery_cycle = models.ForeignKey(
        RecoveryCycle, on_delete=models.CASCADE, related_name="consolidation_checks"
    )
    check_date = models.DateField()
    bone_gap = models.FloatField(validators=[MinValueValidator(0)])
    callus_formation = models.CharField(max_length=20, choices=CALLUS_CHOICES)
    weight_bearing_status = models.CharField(max_length=20, choices=WEIGHT_CHOICES)
    next_check_date = models.DateField()
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    xray_image = models.ImageField(
        upload_to="consolidation_xrays/", blank=True, null=True
    )
    doctor_notes = models.TextField(blank=True, null=True)
    patient_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.recovery_cycle} - {self.check_date}"


# Kilometre taşları
class LengtheningMilestone(models.Model):
    MILESTONE_TYPES = [
        ("distraction_start", "Distraksiyon Başlangıç"),
        ("distraction_end", "Distraksiyon Bitiş"),
        ("partial_weight", "Kısmi Yük"),
        ("full_weight", "Tam Yük"),
        ("device_removal", "Cihaz Çıkarılma"),
        ("physio_start", "Fizyoterapi Başlangıç"),
        ("bone_healing", "Kemik Kaynama"),
        ("full_recovery", "Tam İyileşme"),
    ]

    recovery_cycle = models.ForeignKey(
        RecoveryCycle, on_delete=models.CASCADE, related_name="milestones"
    )
    milestone_date = models.DateField()
    milestone_type = models.CharField(max_length=50, choices=MILESTONE_TYPES)
    achieved_length = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    is_achieved = models.BooleanField(default=False)
    target_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    celebration_note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_achieved and not self.milestone_date:
            self.milestone_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recovery_cycle} - {self.get_milestone_type_display()}"
