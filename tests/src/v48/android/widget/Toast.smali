.class public Landroid/widget/Toast;
.super Ljava/lang/Object;
.source "Toast.java"


# direct methods
.method public constructor <init>()V
    .registers 1

    .prologue
    .line 10
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static makeText(Landroid/content/Context;II)Landroid/widget/Toast;
    .registers 4

    .prologue
    .line 12
    new-instance v0, Landroid/widget/Toast;

    invoke-direct {v0}, Landroid/widget/Toast;-><init>()V

    return-object v0
.end method
