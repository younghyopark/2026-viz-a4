"""
Generate the FOR visualization: "The Education-Employment Paradox"
Left: scatter plot of enrollment gap vs unemployment gap
Right: stacked time series (GPI rising + unemployment gap persisting)
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

with open('processed_data.json') as f:
    data = json.load(f)

countries = data['country_data']
ts = data['timeseries']

# --- FIGURE SETUP ---
fig = plt.figure(figsize=(18, 8), facecolor='white')
gs = gridspec.GridSpec(2, 2, width_ratios=[1.2, 1], height_ratios=[1, 1],
                       hspace=0.25, wspace=0.25)

ax_scatter = fig.add_subplot(gs[:, 0])  # scatter takes full left column
ax_gpi = fig.add_subplot(gs[0, 1])       # top right
ax_unemp = fig.add_subplot(gs[1, 1], sharex=ax_gpi)  # bottom right

# ============================
# LEFT: SCATTER PLOT
# ============================
paradox, others = [], []
for code, d in countries.items():
    eg = d['fem_enroll'] - d['male_enroll']
    ug = d['fem_unemp'] - d['male_unemp']
    (paradox if eg > 0 and ug > 0 else others).append((code, d, eg, ug))

for code, d, eg, ug in others:
    ax_scatter.scatter(eg, ug, c='#bdc3c7', s=70, alpha=0.5, edgecolors='white', linewidth=0.3, zorder=2)
for code, d, eg, ug in paradox:
    ax_scatter.scatter(eg, ug, c='#e74c3c', s=90, alpha=0.78, edgecolors='white', linewidth=0.4, zorder=3)

ax_scatter.spines['left'].set_position('zero')
ax_scatter.spines['bottom'].set_position('zero')
ax_scatter.spines['top'].set_visible(False)
ax_scatter.spines['right'].set_visible(False)
ax_scatter.spines['left'].set_color('#555')
ax_scatter.spines['bottom'].set_color('#555')
ax_scatter.spines['left'].set_linewidth(0.8)
ax_scatter.spines['bottom'].set_linewidth(0.8)

ax_scatter.fill_between([0, 72], 0, 26, color='#e74c3c', alpha=0.04, zorder=1)

q_ur = len(paradox)
q_ul = sum(1 for _, _, eg, ug in others if eg <= 0 and ug > 0)
q_lr = sum(1 for _, _, eg, ug in others if eg > 0 and ug <= 0)
q_ll = sum(1 for _, _, eg, ug in others if eg <= 0 and ug <= 0)
total = len(countries)

ax_scatter.text(39, 17.5, f'{q_ur}/{total} countries ({q_ur*100//total}%)', fontsize=16, fontweight='bold',
        color='#c0392b', ha='center', va='top')
ax_scatter.text(39, 15.5, 'More educated,\nyet more unemployed', fontsize=11,
        color='#c0392b', ha='center', va='top', alpha=0.7, style='italic')
ax_scatter.text(-35, 14, f'{q_ul}/{total} countries', fontsize=12, color='#aaa', ha='center', va='top', fontweight='bold')
ax_scatter.text(52, -8, f'{q_lr}/{total} countries', fontsize=12, color='#aaa', ha='center', va='top', fontweight='bold')
ax_scatter.text(-35, -8, f'{q_ll}/{total} countries', fontsize=12, color='#aaa', ha='center', va='top', fontweight='bold')

for code, (label, dx, dy) in {
    'SAU': ('Saudi Arabia', 10, 4), 'PSE': ('West Bank & Gaza', 10, -6),
    'EGY': ('Egypt', -16, -6), 'DZA': ('Algeria', 8, -5),
    'TUN': ('Tunisia', -14, 2), 'SYR': ('Syria', 8, 4),
    'GRC': ('Greece', -14, 2), 'KWT': ('Kuwait', 8, -6),
}.items():
    if code in countries:
        d = countries[code]
        eg = d['fem_enroll'] - d['male_enroll']
        ug = d['fem_unemp'] - d['male_unemp']
        if eg > 0 and ug > 0:
            ax_scatter.annotate(label, (eg, ug), xytext=(dx, dy), textcoords='offset points',
                        fontsize=10, color='#444', ha='left' if dx > 0 else 'right',
                        arrowprops=dict(arrowstyle='-', color='#bbb', lw=0.5))

ax_scatter.set_xlim(-45, 65)
ax_scatter.set_ylim(-11, 25)
ax_scatter.tick_params(labelsize=11, direction='out', pad=3)
ax_scatter.set_xlabel('Enrollment Gap (Female − Male, pp)', fontsize=12, color='#555', labelpad=6)
ax_scatter.set_ylabel('Unemployment Gap (Female − Male, pp)', fontsize=12, color='#555', labelpad=6)
ax_scatter.xaxis.set_label_coords(0.5, -0.06)
ax_scatter.yaxis.set_label_coords(-0.06, 0.5)

legend_elements = [
    mpatches.Patch(facecolor='#e74c3c', alpha=0.78, label=f'Paradox ({q_ur})'),
    mpatches.Patch(facecolor='#bdc3c7', alpha=0.5, label=f'Other ({total - q_ur})'),
]
ax_scatter.legend(handles=legend_elements, fontsize=11, framealpha=0.95,
          borderpad=0.5, handlelength=1, loc='lower center', ncol=2)

# ============================
# TOP RIGHT: GPI RISING
# ============================
gpi_years = sorted([int(y) for y in ts['WLD']['gpi'].keys()])
gpi_vals = [ts['WLD']['gpi'][str(y)] for y in gpi_years]

ax_gpi.plot(gpi_years, gpi_vals, color='#2980b9', linewidth=2.5)
ax_gpi.fill_between(gpi_years, 0.6, gpi_vals, alpha=0.08, color='#2980b9')
ax_gpi.axhline(1.0, color='#999', linewidth=0.8, linestyle='--', alpha=0.5)
ax_gpi.set_ylabel('Gender Parity Index\n(tertiary enrollment)', fontsize=12, color='#555')
ax_gpi.set_ylim(0.65, 1.18)
ax_gpi.spines['top'].set_visible(False)
ax_gpi.spines['right'].set_visible(False)
ax_gpi.spines['bottom'].set_visible(False)
ax_gpi.tick_params(axis='x', length=0, labelbottom=False)
ax_gpi.tick_params(axis='y', labelsize=11)
ax_gpi.text(2019, 1.14, 'GPI = 1.13', fontsize=11, color='#2980b9', ha='right', fontweight='bold')
ax_gpi.text(1972, 1.03, 'Parity (1.0)', fontsize=10, color='#999', ha='left')
ax_gpi.set_title("Education parity rose...", fontsize=14, fontweight='bold', color='#2c3e50', pad=8, loc='left')
ax_gpi.annotate('', xy=(2018, 1.12), xytext=(1972, 0.75),
            arrowprops=dict(arrowstyle='->', color='#2980b9', lw=2, alpha=0.3))

# ============================
# BOTTOM RIGHT: F vs M UNEMPLOYMENT
# ============================
common_years = sorted(set(int(y) for y in ts['WLD']['fem_unemp'].keys()) & 
                      set(int(y) for y in ts['WLD']['male_unemp'].keys()))
fem_common = [ts['WLD']['fem_unemp'][str(y)] for y in common_years]
male_common = [ts['WLD']['male_unemp'][str(y)] for y in common_years]

ax_unemp.plot(common_years, fem_common, color='#e74c3c', linewidth=2.5, label='Female')
ax_unemp.plot(common_years, male_common, color='#555', linewidth=2.5, label='Male')
ax_unemp.fill_between(common_years, male_common, fem_common,
                 where=[f > m for f, m in zip(fem_common, male_common)],
                 color='#e74c3c', alpha=0.15, label='Gap (F > M)')
ax_unemp.set_ylabel('Unemployment Rate (%)', fontsize=12, color='#555')
ax_unemp.set_xlabel('Year', fontsize=12, color='#555')
ax_unemp.spines['top'].set_visible(False)
ax_unemp.spines['right'].set_visible(False)
ax_unemp.tick_params(labelsize=11)
ax_unemp.legend(fontsize=10, loc='upper right', framealpha=0.95)
ax_unemp.set_title("...but the unemployment gap persisted", fontsize=14, fontweight='bold', color='#c0392b', pad=8, loc='left')
ax_unemp.text(common_years[-1]+0.5, fem_common[-1], f'{fem_common[-1]:.1f}%',
         fontsize=11, color='#e74c3c', va='center', fontweight='bold')
ax_unemp.text(common_years[-1]+0.5, male_common[-1], f'{male_common[-1]:.1f}%',
         fontsize=11, color='#555', va='center', fontweight='bold')

# ============================
# OVERALL TITLE & SOURCE
# ============================
fig.suptitle("The Education–Employment Paradox", fontsize=22, fontweight='bold',
             color='#2c3e50', y=0.98)

fig.text(0.5, 0.005, 'Source: World Bank Development Indicators (1970–2019)  |  Each dot = one country  |  N = 158', 
         fontsize=10, ha='center', color='#aaa')

plt.savefig('viz_for.png', dpi=200, bbox_inches='tight', pad_inches=0.2, facecolor='white')
print("Saved viz_for.png")
