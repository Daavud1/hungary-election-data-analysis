const colors = { blue: '#2563a6', gold: '#d5901a', teal: '#1f8a70', red: '#b1454a', gray: '#768ba0' };
const common = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#e9eff5' }, ticks: { color: '#456078' } }, x: { grid: { display: false }, ticks: { color: '#456078' } } } };

new Chart(document.getElementById('turnoutChart'), {
  type: 'line',
  data: { labels: [1990,1994,1998,2002,2006,2010,2014,2018,2022], datasets: [{ data: [65.1,68.9,56.3,70.5,67.7,64.3,61.7,69.7,69.6], borderColor: colors.blue, backgroundColor: colors.blue, borderWidth: 3, pointRadius: 4, tension: .16 }] },
  options: { ...common, scales: { ...common.scales, y: { ...common.scales.y, min: 50, max: 75, ticks: { callback: value => `${value}%`, color: '#456078' } } }, plugins: { ...common.plugins, tooltip: { callbacks: { label: c => `${c.raw.toFixed(1)}% turnout` } } } }
});

new Chart(document.getElementById('partyChart'), {
  type: 'bar',
  data: { labels: ['TISZA','FIDESZ–KDNP','Mi Hazánk','DK','MKKP'], datasets: [{ data: [53.5,38.9,5.7,1.1,.8], backgroundColor: [colors.blue,colors.gold,colors.teal,colors.red,colors.gray], borderRadius: 3 }] },
  options: { ...common, indexAxis: 'y', scales: { x: { min:0, max:60, ticks: { callback: v => `${v}%`, color:'#456078' }, grid:{color:'#e9eff5'} }, y: { grid:{display:false}, ticks:{color:'#456078'} } } }
});

new Chart(document.getElementById('marginChart'), {
  type: 'bar',
  data: { labels: ['2014','2018','2022','2026'], datasets: [{ data: [16.6,18.2,19.5,18.2], backgroundColor: [colors.gray,colors.blue,colors.gold,colors.teal], borderRadius: 4 }] },
  options: { ...common, scales: { ...common.scales, y: { ...common.scales.y, min:0, ticks: { callback:v => `${v}%`, color:'#456078' }, title: { display:true, text:'Average winner–runner-up margin', color:'#456078' } } }, plugins: { ...common.plugins, tooltip: { callbacks: { label: c => `${c.raw.toFixed(1)} percentage points` } } } }
});
