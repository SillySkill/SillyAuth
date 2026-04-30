/**
 * SillyMD 项目管理页面脚本
 */

document.addEventListener('DOMContentLoaded', async function() {
  // 检查登录 - 使用全局配置
  const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'token';
  const token = localStorage.getItem(tokenKey) || sessionStorage.getItem(tokenKey);
  if (!token) {
    window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.href);
    return;
  }

  // 加载项目列表
  await loadProjects();

  // 初始化新建项目按钮
  initCreateProject();
});

/**
 * 加载项目列表
 */
async function loadProjects() {
  try {
    const response = await VendorAPI.getProjects();

    if (response.success && response.data) {
      const projects = response.data.projects || [];
      renderProjects(projects);
    } else {
      showErrorMessage('加载项目失败');
    }
  } catch (error) {
// console.'加载项目失败:', error);
    showErrorMessage('加载项目失败，请刷新重试');
  }
}

/**
 * 渲染项目列表
 */
function renderProjects(projects) {
  const container = document.querySelector('.page-content');
  const gridContainer = container.querySelector('div[style*="grid-template-columns"]');

  if (!gridContainer) return;

  // 清空现有内容
  gridContainer.innerHTML = '';

  // 渲染项目卡片
  projects.forEach(project => {
    const card = createProjectCard(project);
    gridContainer.appendChild(card);
  });

  // 添加"新建项目"卡片
  const newCard = document.createElement('div');
  newCard.className = 'card';
  newCard.style.cssText = 'border: 2px dashed var(--border-color); background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; min-height: 200px;';
  newCard.innerHTML = `
    <div style="text-align: center; color: var(--text-muted);">
      <i class="fas fa-plus" style="font-size: 48px; margin-bottom: 16px;"></i>
      <p style="font-size: 16px; font-weight: 500;">创建新项目</p>
    </div>
  `;
  newCard.addEventListener('click', showCreateProjectModal);
  gridContainer.appendChild(newCard);
}

/**
 * 创建项目卡片
 */
function createProjectCard(project) {
  const card = document.createElement('div');
  card.className = 'card';
  card.style.cssText = 'padding: 24px;';
  card.dataset.projectId = project.id;

  // 状态映射
  const statusMap = {
    'planned': { text: '规划中', color: 'rgba(245, 158, 11, 0.1)', textColor: 'var(--warning-color)' },
    'in_progress': { text: '进行中', color: 'rgba(16, 185, 129, 0.1)', textColor: 'var(--success-color)' },
    'on_hold': { text: '暂停', color: 'rgba(239, 68, 68, 0.1)', textColor: 'var(--danger-color)' },
    'completed': { text: '已完成', color: 'rgba(59, 130, 246, 0.1)', textColor: 'var(--primary-color)' }
  };

  const status = statusMap[project.project_status] || statusMap['planned'];
  const progress = project.progress || 0;

  card.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
      <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white;">
        <i class="fas fa-rocket"></i>
      </div>
      <span style="padding: 4px 12px; background: ${status.color}; color: ${status.textColor}; border-radius: 20px; font-size: 12px;">
        ${status.text}
      </span>
    </div>
    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">${project.project_name}</h3>
    <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">${project.description || '暂无描述'}</p>
    <div style="width: 100%; height: 6px; background: var(--bg-tertiary); border-radius: 3px; overflow: hidden;">
      <div style="width: ${progress}%; height: 100%; background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); border-radius: 3px;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 8px;">
      <span style="font-size: 12px; color: var(--text-muted);">进度</span>
      <span style="font-size: 12px; color: var(--primary-light); font-weight: 600;">${progress}%</span>
    </div>
  `;

  card.addEventListener('click', () => showProjectDetail(project.id));

  return card;
}

/**
 * 显示项目详情
 */
async function showProjectDetail(projectId) {
  try {
    const response = await VendorAPI.getProjectById(projectId);

    if (response.success && response.data) {
      const project = response.data;
      showProjectModal(project);
    }
  } catch (error) {
// console.'加载项目详情失败:', error);
    showErrorMessage('加载项目详情失败');
  }
}

/**
 * 显示项目模态框
 */
function showProjectModal(project) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  `;

  modal.innerHTML = `
    <div class="card" style="max-width: 800px; width: 90%; max-height: 90vh; overflow-y: auto; padding: 40px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <h2 style="font-size: 1.5rem; font-weight: 700;">${project.project_name}</h2>
        <button class="btn-icon close-modal"><i class="fas fa-times"></i></button>
      </div>

      <div style="margin-bottom: 24px;">
        <label style="font-weight: 600; margin-bottom: 8px; display: block;">项目描述</label>
        <p style="color: var(--text-light);">${project.description || '暂无描述'}</p>
      </div>

      <div style="margin-bottom: 24px;">
        <label style="font-weight: 600; margin-bottom: 8px; display: block;">进度: ${project.progress}%</label>
        <input type="range" id="progressRange" min="0" max="100" value="${project.progress}" style="width: 100%;">
      </div>

      <div style="margin-bottom: 24px;">
        <label style="font-weight: 600; margin-bottom: 8px; display: block;">状态</label>
        <select id="statusSelect" style="width: 100%; padding: 12px; background: var(--bg-dark-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-white);">
          <option value="planned" ${project.project_status === 'planned' ? 'selected' : ''}>规划中</option>
          <option value="in_progress" ${project.project_status === 'in_progress' ? 'selected' : ''}>进行中</option>
          <option value="on_hold" ${project.project_status === 'on_hold' ? 'selected' : ''}>暂停</option>
          <option value="completed" ${project.project_status === 'completed' ? 'selected' : ''}>已完成</option>
        </select>
      </div>

      ${project.skills && project.skills.length > 0 ? `
        <div style="margin-bottom: 24px;">
          <label style="font-weight: 600; margin-bottom: 12px; display: block;">Skills (${project.skills.length})</label>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            ${project.skills.map(skill => `
              <span style="padding: 6px 12px; background: var(--bg-dark-tertiary); border-radius: 20px; font-size: 14px;">
                <i class="fas ${skill.icon || 'fa-star'}" style="margin-right: 4px;"></i>
                ${skill.name}
              </span>
            `).join('')}
          </div>
        </div>
      ` : ''}

      ${project.milestones && project.milestones.length > 0 ? `
        <div style="margin-bottom: 24px;">
          <label style="font-weight: 600; margin-bottom: 12px; display: block;">里程碑 (${project.milestones.length})</label>
          <div style="space-y: 12px;">
            ${project.milestones.map(milestone => `
              <div style="padding: 12px; background: var(--bg-dark-tertiary); border-radius: 8px; margin-bottom: 8px;">
                <div style="font-weight: 600; margin-bottom: 4px;">${milestone.title}</div>
                <div style="font-size: 14px; color: var(--text-light);">
                  ${new Date(milestone.target_date).toLocaleDateString('zh-CN')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 32px;">
        <button class="btn btn-secondary close-modal">取消</button>
        <button class="btn btn-primary" id="saveProject">保存更改</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // 关闭模态框
  modal.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', () => modal.remove());
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  // 保存更改
  document.getElementById('saveProject').addEventListener('click', async () => {
    const progress = document.getElementById('progressRange').value;
    const status = document.getElementById('statusSelect').value;

    try {
      const response = await VendorAPI.updateProject(project.id, {
        progress: parseInt(progress),
        projectStatus: status
      });

      if (response.success) {
        showSuccessMessage('项目更新成功');
        modal.remove();
        await loadProjects(); // 刷新列表
      } else {
        showErrorMessage('更新失败');
      }
    } catch (error) {
// console.'更新项目失败:', error);
      showErrorMessage('更新失败');
    }
  });
}

/**
 * 显示创建项目模态框
 */
function showCreateProjectModal() {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  `;

  modal.innerHTML = `
    <div class="card" style="max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; padding: 40px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <h2 style="font-size: 1.5rem; font-weight: 700;">创建新项目</h2>
        <button class="btn-icon close-modal"><i class="fas fa-times"></i></button>
      </div>

      <form id="createProjectForm">
        <div style="margin-bottom: 16px;">
          <label style="font-weight: 600; margin-bottom: 8px; display: block;">项目名称 *</label>
          <input type="text" id="projectName" required style="width: 100%; padding: 12px; background: var(--bg-dark-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-white);">
        </div>

        <div style="margin-bottom: 16px;">
          <label style="font-weight: 600; margin-bottom: 8px; display: block;">项目标识符 *</label>
          <input type="text" id="projectSlug" required placeholder="例如: my-awesome-project" style="width: 100%; padding: 12px; background: var(--bg-dark-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-white);">
        </div>

        <div style="margin-bottom: 16px;">
          <label style="font-weight: 600; margin-bottom: 8px; display: block;">项目描述</label>
          <textarea id="projectDescription" rows="3" style="width: 100%; padding: 12px; background: var(--bg-dark-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-white); resize: vertical;"></textarea>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
          <button type="button" class="btn btn-secondary close-modal">取消</button>
          <button type="submit" class="btn btn-primary">创建</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);

  // 关闭模态框
  modal.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', () => modal.remove());
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  // 提交表单
  document.getElementById('createProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const projectName = document.getElementById('projectName').value.trim();
    const projectSlug = document.getElementById('projectSlug').value.trim().toLowerCase().replace(/\s+/g, '-');
    const description = document.getElementById('projectDescription').value.trim();

    if (!projectName || !projectSlug) {
      showErrorMessage('请填写必填字段');
      return;
    }

    try {
      const response = await VendorAPI.createProject({
        projectName,
        projectSlug,
        description,
        teamId: 1 // TODO: 从用户数据获取默认团队
      });

      if (response.success) {
        showSuccessMessage('项目创建成功');
        modal.remove();
        await loadProjects(); // 刷新列表
      } else {
        showErrorMessage(response.message || '创建失败');
      }
    } catch (error) {
// console.'创建项目失败:', error);
      showErrorMessage('创建失败');
    }
  });
}

/**
 * 初始化创建项目按钮
 */
function initCreateProject() {
  const createBtn = document.querySelector('.top-actions .btn-primary');
  if (createBtn) {
    createBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showCreateProjectModal();
    });
  }
}

/**
 * 显示成功消息
 */
function showSuccessMessage(message) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    background: #10b981;
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10001;
    animation: slideIn 0.3s ease-out;
  `;
  toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}

/**
 * 显示错误消息
 */
function showErrorMessage(message) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    background: #ef4444;
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10001;
    animation: slideIn 0.3s ease-out;
  `;
  toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}
