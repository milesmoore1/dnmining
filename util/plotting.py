"""Classification diagnostic plots; presentation defaults live here."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import (
    confusion_matrix, precision_recall_fscore_support,
    roc_curve, auc, precision_recall_curve,
)


def plot_classifier_diagnostics(model, X_test, y_test, feature_names, class_names):
    """Display and return the diagnostic, probability, and importance figures."""
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test) 

    CLASS_COLORS = ["#2a78d6", "#e34948"]
    INK_PRIMARY, INK_SECONDARY, INK_MUTED = "#0b0b0b", "#52514e", "#898781"
    GRIDLINE, SURFACE = "#e1e0d9", "#fcfcfb"
    BLUE, RED = "#2a78d6", "#e34948"          # diverging pair -- low/high as opposite poles
    CAT = {"precision": "#2a78d6", "recall": "#eb6834", "f1": "#1baf7a"}
    seq_cmap = LinearSegmentedColormap.from_list("seq_blue", ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"])

    cm = confusion_matrix(y_test, preds, labels=list(range(len(class_names))))
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, labels=list(range(len(class_names))), zero_division=0)
    # Each curve compares one class against the other class.

    fig, axes = plt.subplots(2, 2, figsize=(11, 10), facecolor=SURFACE)

    # ---- confusion matrix ----
    ax = axes[0, 0]; ax.set_facecolor(SURFACE)
    cm_pct = cm / cm.sum(axis=1, keepdims=True)
    im = ax.imshow(cm_pct, cmap=seq_cmap, vmin=0, vmax=1)
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            color = "white" if cm_pct[i, j] > 0.6 else INK_PRIMARY
            ax.text(j, i, f"{cm[i, j]}\n({cm_pct[i, j]:.0%})", ha="center", va="center", color=color, fontsize=11)
    ax.set_xticks(range(len(class_names))); ax.set_xticklabels(class_names, color=INK_SECONDARY)
    ax.set_yticks(range(len(class_names))); ax.set_yticklabels(class_names, color=INK_SECONDARY)
    ax.set_xlabel("Predicted", color=INK_SECONDARY); ax.set_ylabel("Actual", color=INK_SECONDARY)
    ax.set_title("Confusion matrix", color=INK_PRIMARY, fontsize=12, loc="left")
    for s in ax.spines.values(): s.set_visible(False)

    # ---- precision / recall / f1 ----
    ax2 = axes[0, 1]; ax2.set_facecolor(SURFACE)
    x = np.arange(len(class_names)); width = 0.25
    groups = [
        ax2.bar(x - width, precision, width, label="precision", color=CAT["precision"]),
        ax2.bar(x,          recall,   width, label="recall",    color=CAT["recall"]),
        ax2.bar(x + width,  f1,       width, label="f1",        color=CAT["f1"]),
    ]
    for g in groups:
        for b in g:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width()/2, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=8, color=INK_SECONDARY)
    ax2.set_xticks(x); ax2.set_xticklabels(class_names, color=INK_SECONDARY)
    ax2.set_ylim(0, 1.1); ax2.set_ylabel("score", color=INK_SECONDARY)
    ax2.set_title("Precision / recall / F1", color=INK_PRIMARY, fontsize=12, loc="left")
    ax2.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
    ax2.grid(axis="y", color=GRIDLINE, linewidth=0.8, zorder=0); ax2.set_axisbelow(True)
    for s in ax2.spines.values(): s.set_visible(False)

    # ---- ROC curve ----
    ax3 = axes[1, 0]; ax3.set_facecolor(SURFACE)
    for class_id, (name, color) in enumerate(zip(class_names, CLASS_COLORS)):
        fpr, tpr, _ = roc_curve(y_test == class_id, proba[:, class_id])
        roc_auc = auc(fpr, tpr)
        ax3.plot(fpr, tpr, color=color, linewidth=2, label=f"{name} vs rest (AUC = {roc_auc:.3f})")
    ax3.plot([0, 1], [0, 1], color=INK_MUTED, linewidth=1.5, linestyle="--", label="chance")
    ax3.set_xlabel("False positive rate", color=INK_SECONDARY)
    ax3.set_ylabel("True positive rate", color=INK_SECONDARY)
    ax3.set_title("ROC curve", color=INK_PRIMARY, fontsize=12, loc="left")
    ax3.legend(frameon=False, loc="lower right")
    ax3.grid(color=GRIDLINE, linewidth=0.8, zorder=0); ax3.set_axisbelow(True)
    for s in ax3.spines.values(): s.set_visible(False)

    # ---- precision-recall curve ----
    ax4 = axes[1, 1]; ax4.set_facecolor(SURFACE)
    for class_id, (name, color) in enumerate(zip(class_names, CLASS_COLORS)):
        actual = y_test == class_id
        prec_curve, rec_curve, _ = precision_recall_curve(actual, proba[:, class_id])
        ax4.plot(rec_curve, prec_curve, color=color, linewidth=2, label=f"{name} vs rest")
        ax4.axhline(actual.mean(), color=color, linewidth=1, linestyle="--", alpha=0.5)
    ax4.set_xlabel("Recall", color=INK_SECONDARY); ax4.set_ylabel("Precision", color=INK_SECONDARY)
    ax4.set_title("Precision-recall curve", color=INK_PRIMARY, fontsize=12, loc="left")
    ax4.legend(frameon=False, loc="lower left")
    ax4.grid(color=GRIDLINE, linewidth=0.8, zorder=0); ax4.set_axisbelow(True)
    for s in ax4.spines.values(): s.set_visible(False)

    plt.tight_layout()
    plt.show()

    # ---- predicted probability, split by actual class ----
    fig2, ax5 = plt.subplots(figsize=(8, 4.5), facecolor=SURFACE)
    ax5.set_facecolor(SURFACE)
    for class_id, (name, color) in enumerate(zip(class_names, CLASS_COLORS)):
        ax5.hist(proba[y_test == class_id, 1], bins=np.linspace(0, 1, 31), alpha=0.55, color=color, label=f"actual: {name}")
    ax5.set_xlabel("Predicted P(high)", color=INK_SECONDARY)
    ax5.set_ylabel("count", color=INK_SECONDARY)
    ax5.set_title("Predicted probability by actual class", color=INK_PRIMARY, fontsize=12, loc="left")
    ax5.legend(frameon=False)
    for s in ax5.spines.values(): s.set_visible(False)
    plt.tight_layout()
    plt.show()

    # ---- feature importance ----
    importances = model.feature_importances_
    order = np.argsort(importances)[-15:]  # top 15
    fig3, ax6 = plt.subplots(figsize=(7, 6), facecolor=SURFACE)
    ax6.set_facecolor(SURFACE)
    ax6.barh(np.array(feature_names)[order], importances[order], color=BLUE)
    ax6.set_xlabel("importance (gain)", color=INK_SECONDARY)
    ax6.set_title("Top 15 features", color=INK_PRIMARY, fontsize=12, loc="left")
    ax6.tick_params(colors=INK_SECONDARY)
    for s in ax6.spines.values(): s.set_visible(False)
    plt.tight_layout()
    plt.show()
    return fig, fig2, fig3
