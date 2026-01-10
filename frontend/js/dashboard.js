// Dashboard functionality with tier-specific displays

document.addEventListener('DOMContentLoaded', function () {
  // Get manager info
  const manager = AuthManager.getManager();
  const tier = manager?.tier || 'small';
  const managerId = manager?.id;

  // Set manager info in header
  document.getElementById('managerName').textContent = manager?.name || 'Manager';
  document.getElementById('managerTier').textContent = tier.charAt(0).toUpperCase() + tier.slice(1) + ' Tier';

  // Set tier badge
  const tierBadge = document.getElementById('tierBadge');
  tierBadge.textContent = tier.toUpperCase() + ' TIER';
  tierBadge.className = `tier-badge ${tier}`;

  // Load data based on tier
  loadDashboardData(tier, managerId);
});

async function loadDashboardData(tier, managerId) {
  try {
    // Try to fetch from RDS
    const casesData = await fetchCasesFromRDS(managerId, tier);
    
    // Get mock stats (you can also create a Lambda for stats)
    const mockData = getMockDataByTier(tier);
    
    // Display stats
    displayStats(mockData.stats);
    
    // Display main table with RDS data
    displayMainTable(casesData);
    
    // Display secondary tables if applicable
    if (mockData.secondaryTables) {
      displaySecondaryTables(mockData.secondaryTables);
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    // Fallback to mock data
    const mockData = getMockDataByTier(tier);
    displayStats(mockData.stats);
    displayMainTable(mockData.mainTable);
    if (mockData.secondaryTables) {
      displaySecondaryTables(mockData.secondaryTables);
    }
  }
}

async function fetchCasesFromRDS(managerId, tier) {
  try {
    const endpoint = `/api/manager/cases?manager_id=${managerId}&tier=${tier}`;
    const response = await API.request(endpoint, { method: 'GET' });
    
    if (response.success && response.cases) {
      // Transform RDS data to match table format
      return response.cases.map(caseData => ({
        id: caseData.case_id || caseData.id,
        caseNumber: caseData.case_number || '#' + (caseData.case_id || 'N/A'),
        debtor: caseData.debtor_name || 'N/A',
        amount: '$' + (caseData.amount_owed || 0).toFixed(2),
        status: caseData.status || 'pending',
        date: caseData.created_date || new Date().toLocaleDateString(),
        activity: caseData.last_activity || 'N/A'
      }));
    }
    
    return [];
  } catch (error) {
    console.error('Error fetching cases from RDS:', error);
    throw error;
  }
}

function getMockDataByTier(tier) {
  const baseData = {
    stats: [
      { label: 'Total Cases', value: 156, change: '+12%' },
      { label: 'Active Cases', value: 89, change: '+5%' },
      { label: 'Closed Cases', value: 67, change: '+8%' }
    ],
    mainTable: {
      title: 'Recent Cases',
      columns: ['Case ID', 'Debtor Name', 'Amount', 'Status'],
      rows: [
        { id: 'CASE-001', name: 'John Smith', amount: '$5,000', status: 'active' },
        { id: 'CASE-002', name: 'Jane Doe', amount: '$3,500', status: 'active' },
        { id: 'CASE-003', name: 'Bob Johnson', amount: '$7,200', status: 'closed' },
        { id: 'CASE-004', name: 'Sarah Williams', amount: '$4,800', status: 'pending' },
        { id: 'CASE-005', name: 'Mike Brown', amount: '$6,100', status: 'active' }
      ]
    }
  };

  // Tier-specific customizations
  switch (tier) {
    case 'small':
      return {
        ...baseData,
        stats: baseData.stats.slice(0, 3)
      };

    case 'mid':
      return {
        ...baseData,
        stats: [
          { label: 'Total Cases', value: 245, change: '+15%' },
          { label: 'Active Cases', value: 178, change: '+8%' },
          { label: 'Closed Cases', value: 67, change: '+10%' },
          { label: 'Recovery Rate', value: '68%', change: '+5%' }
        ],
        mainTable: {
          ...baseData.mainTable,
          rows: baseData.mainTable.rows.concat([
            { id: 'CASE-006', name: 'Lisa Anderson', amount: '$5,500', status: 'active' },
            { id: 'CASE-007', name: 'Tom Harris', amount: '$8,900', status: 'pending' }
          ])
        }
      };

    case 'large':
      return {
        ...baseData,
        stats: [
          { label: 'Total Cases', value: 589, change: '+22%' },
          { label: 'Active Cases', value: 412, change: '+18%' },
          { label: 'Closed Cases', value: 177, change: '+15%' },
          { label: 'Total Recovered', value: '$2.5M', change: '+12%' },
          { label: 'Avg Recovery Time', value: '38 days', change: '-3 days' },
          { label: 'Success Rate', value: '92%', change: '+8%' }
        ],
        mainTable: {
          ...baseData.mainTable,
          title: 'Top Cases by Amount',
          columns: ['Case ID', 'Debtor Name', 'Amount', 'Recovery %', 'Status'],
          rows: [
            { id: 'CASE-001', name: 'John Smith', amount: '$5,000', recovery: '85%', status: 'active' },
            { id: 'CASE-002', name: 'Jane Doe', amount: '$3,500', recovery: '60%', status: 'active' },
            { id: 'CASE-003', name: 'Bob Johnson', amount: '$7,200', recovery: '100%', status: 'closed' },
            { id: 'CASE-004', name: 'Sarah Williams', amount: '$4,800', recovery: '45%', status: 'pending' },
            { id: 'CASE-005', name: 'Mike Brown', amount: '$6,100', recovery: '90%', status: 'active' }
          ]
        },
        secondaryTables: [
          {
            title: 'Recovery Reports',
            columns: ['Month', 'Total Recovered', 'Case Count', 'Avg Recovery'],
            rows: [
              { month: 'January', recovered: '$45,000', cases: 12, avg: '$3,750' },
              { month: 'December', recovered: '$52,000', cases: 15, avg: '$3,467' },
              { month: 'November', recovered: '$38,000', cases: 10, avg: '$3,800' }
            ]
          }
        ]
      };

    case 'mega':
      return {
        ...baseData,
        stats: [
          { label: 'Total Cases', value: 1245, change: '+32%' },
          { label: 'Active Cases', value: 856, change: '+25%' },
          { label: 'Total Recovered', value: '$8.7M', change: '+28%' },
          { label: 'Agencies', value: 12, change: '+2' },
          { label: 'Recovery Rate', value: '89%', change: '+12%' },
          { label: 'Managers', value: 45, change: '+8%' }
        ],
        mainTable: {
          ...baseData.mainTable,
          title: 'Critical Cases',
          columns: ['Case ID', 'Debtor Name', 'Amount', 'Age (days)', 'Status'],
          rows: [
            { id: 'CASE-101', name: 'John Smith', amount: '$25,000', age: 92, status: 'active' },
            { id: 'CASE-102', name: 'Jane Doe', amount: '$18,500', age: 76, status: 'active' },
            { id: 'CASE-103', name: 'Bob Johnson', amount: '$32,200', age: 124, status: 'active' },
            { id: 'CASE-104', name: 'Sarah Williams', amount: '$14,800', age: 45, status: 'pending' },
            { id: 'CASE-105', name: 'Mike Brown', amount: '$22,100', age: 67, status: 'active' }
          ]
        },
        secondaryTables: [
          {
            title: 'Agency Performance',
            columns: ['Agency', 'Cases', 'Recovered', 'Success Rate', 'Ranking'],
            rows: [
              { agency: 'Chicago Office', cases: 245, recovered: '$890,000', rate: '89%', rank: '1st' },
              { agency: 'New York Office', cases: 198, recovered: '$756,000', rate: '87%', rank: '2nd' },
              { agency: 'Boston Office', cases: 167, recovered: '$645,000', rate: '85%', rank: '3rd' }
            ]
          },
          {
            title: 'Monthly KPIs',
            columns: ['KPI', 'Current', 'Target', '% Complete', 'Status'],
            rows: [
              { kpi: 'Monthly Revenue', current: '$125,000', target: '$150,000', percent: '83%', status: 'pending' },
              { kpi: 'Case Resolution', current: '156 cases', target: '180 cases', percent: '87%', status: 'active' },
              { kpi: 'Customer Satisfaction', current: '94%', target: '95%', percent: '99%', status: 'active' }
            ]
          }
        ]
      };

    default:
      return baseData;
  }
}

function displayStats(stats) {
  const container = document.getElementById('statsCards');
  container.innerHTML = stats.map(stat => `
    <div class="stat-card">
      <div class="stat-label">${stat.label}</div>
      <div class="stat-value">${stat.value}</div>
      <div class="stat-change">${stat.change}</div>
    </div>
  `).join('');
}

function displayMainTable(tableConfig) {
  const tableTitle = document.getElementById('tableTitle');
  const tableHead = document.getElementById('tableHead');
  const tableBody = document.getElementById('tableBody');

  tableTitle.textContent = tableConfig.title;

  // Build header
  const columns = tableConfig.columns;
  tableHead.innerHTML = `
    <tr>
      ${columns.map(col => `<th>${col}</th>`).join('')}
    </tr>
  `;

  // Build body
  tableBody.innerHTML = tableConfig.rows.map(row => {
    const values = Object.values(row);
    const status = row.status || row.tier || row.rank || '';
    
    return `
      <tr>
        ${Object.keys(row).map(key => {
          const value = row[key];
          if (key === 'status') {
            return `<td><span class="status-badge ${value}">${value}</span></td>`;
          }
          return `<td>${value}</td>`;
        }).join('')}
      </tr>
    `;
  }).join('');
}

function displaySecondaryTables(tables) {
  const container = document.getElementById('secondaryTableSection');
  
  container.innerHTML = tables.map((tableConfig, index) => `
    <h2 class="section-title">${tableConfig.title}</h2>
    <div class="table-wrapper">
      <div class="table-header">
        <h3 class="table-title">${tableConfig.title}</h3>
      </div>
      <table>
        <thead>
          <tr>
            ${tableConfig.columns.map(col => `<th>${col}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${tableConfig.rows.map(row => `
            <tr>
              ${Object.keys(row).map(key => {
                const value = row[key];
                if (key === 'status' || key === 'rank') {
                  return `<td><span class="status-badge ${value}">${value}</span></td>`;
                }
                return `<td>${value}</td>`;
              }).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `).join('');
}

function refreshData() {
  const manager = AuthManager.getManager();
  loadDashboardData(manager?.tier || 'small');
  
  // Show refresh feedback
  alert('Data refreshed!');
}

function handleLogout() {
  if (confirm('Are you sure you want to logout?')) {
    AuthManager.logout();
    window.location.href = 'signin.html';
  }
}
