"""
Generate the AGAINST visualization: "No Paradox — Education Progress
IS Translating Into Employment Equality"

Layout:
  - Top: World map choropleth — green = no paradox, red = paradox (MENA cluster)
  - Bottom-left: Histogram of unemployment gaps (most near zero)
  - Bottom-right: Success stories bar chart
  - Right column: Big-number callout stats
"""

import json
import csv
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import geopandas as gpd

with open('processed_data.json') as f:
    data = json.load(f)

countries = data['country_data']
ts = data['timeseries']

# ---------- classify countries ----------
classify = {}  # code -> category
for code, d in countries.items():
    eg = d['fem_enroll'] - d['male_enroll']
    ug = d['fem_unemp'] - d['male_unemp']
    if eg > 0 and ug <= 0:
        classify[code] = 'success'      # more educated AND equal/better employment
    elif abs(ug) <= 3:
        classify[code] = 'near_equal'   # near-equal unemployment (within 3pp)
    elif eg > 0 and ug > 0:
        classify[code] = 'paradox'      # "paradox" countries
    else:
        classify[code] = 'other'

# ---------- colour palette ----------
C_SUCCESS  = '#27ae60'   # strong green — education works
C_NEAR_EQ  = '#a8e6cf'   # light green — near-equal, no problem
C_PARADOX  = '#dcdde1'   # same gray — merged with other
C_OTHER    = '#dcdde1'   # neutral gray
C_NODATA   = '#f0f0f0'   # very light for no-data countries
C_DARK     = '#2c3e50'
C_GRAY     = '#95a5a6'
C_LIGHT    = '#ecf0f1'
C_BG       = 'white'

# ---------- load map ----------
world = gpd.read_file('ne_110m_countries.gpkg')
# Build lookup: try ISO_A3, then ADM0_A3, then WB_A3
def get_category(row):
    for col in ['ISO_A3', 'ADM0_A3', 'WB_A3']:
        code = row[col]
        if code in classify:
            return classify[code]
    return 'nodata'

world['category'] = world.apply(get_category, axis=1)

COLOR_MAP = {
    'success': C_SUCCESS,
    'near_equal': C_NEAR_EQ,
    'paradox': C_PARADOX,
    'other': C_OTHER,
    'nodata': C_NODATA,
}
world['color'] = world['category'].map(COLOR_MAP)

# Count stats
n_success = sum(1 for v in classify.values() if v == 'success')
n_near = sum(1 for v in classify.values() if v == 'near_equal')
n_paradox = sum(1 for v in classify.values() if v == 'paradox')
n_no_paradox = n_success + n_near  # countries where education works or gap is tiny
total = len(countries)

# =====================================================
# FIGURE SETUP
# =====================================================
fig = plt.figure(figsize=(18, 13), facecolor=C_BG)

outer = gridspec.GridSpec(2, 1, height_ratios=[1.4, 1],
                          hspace=0.25,
                          left=0.06, right=0.96, top=0.93, bottom=0.06)

ax_map = fig.add_subplot(outer[0, 0])   # top: map

# Bottom: two time-series panels side by side
bottom_gs = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[1, 0],
                                              wspace=0.25)
ax_gpi   = fig.add_subplot(bottom_gs[0, 0])
ax_unemp = fig.add_subplot(bottom_gs[0, 1])

# =====================================================
# TOP: WORLD MAP CHOROPLETH
# =====================================================
world.plot(ax=ax_map, color=world['color'], edgecolor='white', linewidth=0.3)

# Remove axes
ax_map.set_xlim(-170, 180)
ax_map.set_ylim(-60, 85)
ax_map.axis('off')

# Title
ax_map.set_title('Where Women Are More Educated, Employment Follows',
                  fontsize=20, fontweight='bold', color=C_DARK, pad=12, loc='center')

# Map legend
n_other_all = total - n_success - n_near
legend_items = [
    mpatches.Patch(facecolor=C_SUCCESS, edgecolor='white', label=f'Education leads to employment ({n_success})'),
    mpatches.Patch(facecolor=C_NEAR_EQ, edgecolor='white', label=f'Near-equal unemployment, within 3pp ({n_near})'),
    mpatches.Patch(facecolor=C_OTHER, edgecolor='#ccc', label=f'Other ({n_other_all})'),
]
ax_map.legend(handles=legend_items, fontsize=13, loc='lower left',
              framealpha=0.95, borderpad=0.8, handlelength=1.5,
              handletextpad=0.8, labelspacing=0.6,
              bbox_to_anchor=(0.0, -0.02))


# =====================================================
# Compute combined average for green regions (EAS, ECS, NAC)
# =====================================================
GREEN_CODES = ['EAS', 'ECS', 'NAC']

# Enrollment: average F and M across green regions
enroll_years = sorted(y for y in range(1970, 2020)
                      if all(str(y) in ts[c]['fem_enroll'] and str(y) in ts[c]['male_enroll']
                             for c in GREEN_CODES))
fem_enroll = [np.mean([ts[c]['fem_enroll'][str(y)] for c in GREEN_CODES]) for y in enroll_years]
male_enroll = [np.mean([ts[c]['male_enroll'][str(y)] for c in GREEN_CODES]) for y in enroll_years]

# Unemployment: average F and M across green regions
unemp_all_years = set()
for code in GREEN_CODES:
    unemp_all_years |= (set(int(y) for y in ts[code]['fem_unemp'].keys()) &
                         set(int(y) for y in ts[code]['male_unemp'].keys()))
unemp_years = sorted(y for y in unemp_all_years
                     if all(str(y) in ts[c]['fem_unemp'] and str(y) in ts[c]['male_unemp']
                            for c in GREEN_CODES))
fem_avg = [np.mean([ts[c]['fem_unemp'][str(y)] for c in GREEN_CODES]) for y in unemp_years]
male_avg = [np.mean([ts[c]['male_unemp'][str(y)] for c in GREEN_CODES]) for y in unemp_years]

# =====================================================
# BOTTOM LEFT: Female vs Male enrollment (crossover story)
# =====================================================
ax_gpi.plot(enroll_years, fem_enroll, color=C_SUCCESS, linewidth=2.8, label='Female')
ax_gpi.plot(enroll_years, male_enroll, color=C_DARK, linewidth=2.8, label='Male')
ax_gpi.fill_between(enroll_years, male_enroll, fem_enroll,
                     where=[f >= m for f, m in zip(fem_enroll, male_enroll)],
                     color=C_SUCCESS, alpha=0.15)

ax_gpi.set_ylabel('Tertiary Enrollment Rate (%)', fontsize=12, color=C_DARK)
ax_gpi.spines['top'].set_visible(False)
ax_gpi.spines['right'].set_visible(False)
ax_gpi.tick_params(labelsize=11)
ax_gpi.set_xlabel('Year', fontsize=12, color=C_DARK)
ax_gpi.set_title('Women surpassed men in education...', fontsize=15, fontweight='bold',
                  color=C_DARK, pad=8, loc='left')
ax_gpi.legend(fontsize=10, loc='upper left', framealpha=0.95)

# End-point labels
ax_gpi.text(enroll_years[-1] + 1, fem_enroll[-1], f'{fem_enroll[-1]:.0f}%',
            fontsize=11, color=C_SUCCESS, fontweight='bold', va='center')
ax_gpi.text(enroll_years[-1] + 1, male_enroll[-1], f'{male_enroll[-1]:.0f}%',
            fontsize=11, color=C_DARK, fontweight='bold', va='center')

# Crossover annotation
cross_yr = next(y for y, f, m in zip(enroll_years, fem_enroll, male_enroll) if f > m)
cross_val = next(f for y, f, m in zip(enroll_years, fem_enroll, male_enroll) if f > m)
ax_gpi.annotate(f'Women overtake\nmen ({cross_yr})',
                xy=(cross_yr, cross_val), xytext=(cross_yr - 8, cross_val + 18),
                fontsize=10, color=C_SUCCESS, fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', color=C_SUCCESS, lw=1.5))

ax_gpi.text(0.5, 0.05, 'Average: East Asia, Europe & North America',
            fontsize=9, color=C_GRAY, ha='center', va='center',
            transform=ax_gpi.transAxes, style='italic')

# =====================================================
# BOTTOM RIGHT: Female labor force participation rising
# =====================================================
# Extract "Labor force, female (% of total labor force)" from raw CSV
with open('education-raw-2021.csv', errors='replace') as f:
    raw_lines = f.readlines()

raw_header = next(csv.reader(io.StringIO(raw_lines[4])))
year_cols = {}
for i, col in enumerate(raw_header):
    if col.strip().isdigit() and 1960 <= int(col.strip()) <= 2021:
        year_cols[int(col.strip())] = i

labor_data = {}  # code -> {year: value}
for line in raw_lines[5:]:
    row = next(csv.reader(io.StringIO(line)))
    if len(row) < 5:
        continue
    code, indicator = row[1], row[2]
    if code in ('EAS', 'ECS', 'NAC') and indicator == 'Labor force, female (% of total labor force)':
        vals = {}
        for yr, col_idx in year_cols.items():
            if col_idx < len(row) and row[col_idx].strip():
                try:
                    vals[yr] = float(row[col_idx])
                except ValueError:
                    pass
        labor_data[code] = vals

# Compute average across green regions
labor_years = sorted(y for y in range(1990, 2020)
                     if all(y in labor_data.get(c, {}) for c in GREEN_CODES))
labor_avg = [np.mean([labor_data[c][y] for c in GREEN_CODES]) for y in labor_years]

ax_unemp.plot(labor_years, labor_avg, color=C_SUCCESS, linewidth=2.8)
ax_unemp.fill_between(labor_years, min(labor_avg) - 0.5, labor_avg,
                        alpha=0.10, color=C_SUCCESS)

ax_unemp.set_ylabel("Women's Share of\nLabor Force (%)", fontsize=12, color=C_DARK)
ax_unemp.set_xlabel('Year', fontsize=12, color=C_DARK)
ax_unemp.spines['top'].set_visible(False)
ax_unemp.spines['right'].set_visible(False)
ax_unemp.tick_params(labelsize=11)
ax_unemp.set_title('...and women entered the workforce', fontsize=15, fontweight='bold',
                     color=C_SUCCESS, pad=8, loc='left')

# End-point labels
ax_unemp.text(labor_years[0] - 0.5, labor_avg[0], f'{labor_avg[0]:.1f}%',
              fontsize=11, color=C_GRAY, fontweight='bold', va='center', ha='right')
ax_unemp.text(labor_years[-1] + 0.8, labor_avg[-1], f'{labor_avg[-1]:.1f}%',
              fontsize=11, color=C_SUCCESS, fontweight='bold', va='center')

# Trend arrow annotation
ax_unemp.annotate('', xy=(2018, labor_avg[-1]), xytext=(1992, labor_avg[0]),
                   arrowprops=dict(arrowstyle='->', color=C_SUCCESS, lw=2, alpha=0.3))

ax_unemp.text(0.5, 0.08, 'Average: East Asia, Europe & North America',
              fontsize=9, color=C_GRAY, ha='center', va='center',
              transform=ax_unemp.transAxes, style='italic')

# =====================================================
# SOURCE FOOTNOTE
# =====================================================
fig.text(0.5, 0.01,
         'Source: World Bank Development Indicators (1970\u20132019)  |  '
         f'N = {total} countries',
         fontsize=10, ha='center', color=C_GRAY)

plt.savefig('viz_against.png', dpi=200, bbox_inches='tight', pad_inches=0.3, facecolor=C_BG)
print("Saved viz_against.png")
