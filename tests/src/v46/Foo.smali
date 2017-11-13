.class public LFoo;
.super Ljava/lang/Object;
.source "Foo.java"


# direct methods
.method public constructor <init>()V
    .registers 1

    .prologue
    .line 8
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public bar()V
    .registers 4

    .prologue
    .line 11
    const/4 v0, 0x0

    const v1, 0x1e240

    const/4 v2, 0x1

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;II)Landroid/widget/Toast;

    .line 12
    return-void
.end method
