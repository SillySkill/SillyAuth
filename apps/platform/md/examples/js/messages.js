/**
 * SillyMD 消息系统
 * 提供消息和通信功能
 */

(function(global) {
  'use strict';

  const MessageAPI = {
    config: {
      // 使用全局配置或默认值
      get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_BASE : 'http://47.96.133.238:8000';
      },
      get timeout() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_TIMEOUT : 10000;
      },
      currentUserId: 1 // TODO: 从认证系统获取真实用�?ID
    },

    state: {
      currentConversationId: null,
      conversations: [],
      messages: {},
      unreadCount: 0,
      pollingInterval: null
    },

    /**
     * 初始化消息系�?     */
    async init() {
// // console.log('📨 消息系统初始�?..');

      try {
        // 加载对话列表
        await this.loadConversations();

        // 加载未读消息�?        await this.updateUnreadCount();

        // 开始轮�?        this.startPolling();

// // console.log('�?消息系统初始化完�?);
      } catch (error) {
// console.'�?消息系统初始化失�?', error);
        throw error;
      }
    },

    /**
     * 加载对话列表
     */
    async loadConversations() {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/conversations?limit=50`, {
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        this.state.conversations = await response.json();
        this.renderConversations();

        return this.state.conversations;
      } catch (error) {
// console.'加载对话列表失败:', error);
        throw error;
      }
    },

    /**
     * 加载对话消息
     */
    async loadMessages(conversationId, beforeId = null) {
      try {
        let url = `${this.config.apiBaseUrl}/api/conversations/${conversationId}/messages?limit=50`;
        if (beforeId) {
          url += `&before_id=${beforeId}`;
        }

        const response = await fetch(url, {
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const messages = await response.json();

        // 缓存消息
        if (!this.state.messages[conversationId]) {
          this.state.messages[conversationId] = [];
        }

        if (beforeId) {
          // 加载历史消息，添加到开�?          this.state.messages[conversationId] = [...messages, ...this.state.messages[conversationId]];
        } else {
          // 新消息或首次加载
          const existingIds = new Set(this.state.messages[conversationId].map(m => m.id));
          const newMessages = messages.filter(m => !existingIds.has(m.id));
          this.state.messages[conversationId] = [...this.state.messages[conversationId], ...newMessages];
        }

        return messages;
      } catch (error) {
// console.'加载消息失败:', error);
        throw error;
      }
    },

    /**
     * 发送消�?     */
    async sendMessage(conversationId, content, messageType = 'text', replyToId = null, attachments = null) {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            content: content,
            message_type: messageType,
            reply_to_id: replyToId,
            attachments: attachments
          }),
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // 重新加载消息
        await this.loadMessages(conversationId);

        // 刷新对话列表以更新最后消�?        await this.loadConversations();

        return result;
      } catch (error) {
// console.'发送消息失�?', error);
        throw error;
      }
    },

    /**
     * 创建新对�?     */
    async createConversation(conversationType, title, participantIds, initialMessage = null) {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/conversations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            conversation_type: conversationType,
            title: title,
            participant_ids: participantIds,
            initial_message: initialMessage
          }),
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // 重新加载对话列表
        await this.loadConversations();

        return result;
      } catch (error) {
// console.'创建对话失败:', error);
        throw error;
      }
    },

    /**
     * 标记对话为已�?     */
    async markConversationRead(conversationId) {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/conversations/${conversationId}/read`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // 更新本地状�?        const conversation = this.state.conversations.find(c => c.id === conversationId);
        if (conversation) {
          conversation.has_unread = false;
          conversation.unread_count = 0;
          this.renderConversations();
        }

        // 更新未读�?        await this.updateUnreadCount();

        return await response.json();
      } catch (error) {
// console.'标记已读失败:', error);
        throw error;
      }
    },

    /**
     * 更新未读消息�?     */
    async updateUnreadCount() {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/conversations/unread-count`, {
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        this.state.unreadCount = result.unread_count;

        // 更新通知图标
        this.updateUnreadBadge();

        return result;
      } catch (error) {
// console.'获取未读数失�?', error);
        throw error;
      }
    },

    /**
     * 删除对话
     */
    async deleteConversation(conversationId) {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/conversations/${conversationId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(this.config.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // 从列表中移除
        this.state.conversations = this.state.conversations.filter(c => c.id !== conversationId);
        this.renderConversations();

        return await response.json();
      } catch (error) {
// console.'删除对话失败:', error);
        throw error;
      }
    },

    /**
     * 开始轮�?     */
    startPolling() {
      // �?5 秒轮询一�?      this.state.pollingInterval = setInterval(async () => {
        try {
          // 检查当前对话的新消�?          if (this.state.currentConversationId) {
            await this.loadMessages(this.state.currentConversationId);
            this.renderMessages();
          }

          // 更新对话列表
          await this.loadConversations();

          // 更新未读�?          await this.updateUnreadCount();
        } catch (error) {
// console.'轮询更新失败:', error);
        }
      }, 5000);
    },

    /**
     * 停止轮询
     */
    stopPolling() {
      if (this.state.pollingInterval) {
        clearInterval(this.state.pollingInterval);
        this.state.pollingInterval = null;
      }
    },

    /**
     * 渲染对话列表
     */
    renderConversations() {
      const container = document.querySelector('[data-conversations-list]');
      if (!container) return;

      if (this.state.conversations.length === 0) {
        container.innerHTML = `
          <div style="padding: 40px 20px; text-align: center; color: var(--text-muted);">
            <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 12px; opacity: 0.5;"></i>
            <p>暂无对话</p>
          </div>
        `;
        return;
      }

      container.innerHTML = this.state.conversations.map(conv => {
        const isActive = conv.id === this.state.currentConversationId;
        const unreadBadge = conv.unread_count > 0
          ? `<span class="unread-badge">${conv.unread_count}</span>`
          : '';

        // 获取显示名称（非群聊时显示另一个用户名�?        let displayName = conv.title || '未命名对�?;
        let avatarInitial = displayName.charAt(0);

        if (!conv.is_group && conv.participants && conv.participants.length === 2) {
          const otherUser = conv.participants.find(p => p.user_id !== this.config.currentUserId);
          if (otherUser) {
            displayName = otherUser.username;
            avatarInitial = displayName.charAt(0);
          }
        }

        const lastMessage = conv.last_message_content
          ? this.truncateText(conv.last_message_content, 30)
          : '暂无消息';

        return `
          <div class="conversation-item ${isActive ? 'active' : ''}"
               data-conversation-id="${conv.id}"
               onclick="MessageAPI.selectConversation(${conv.id})">
            <div class="conversation-avatar" style="background: ${this.getAvatarColor(conv.id)}">
              ${avatarInitial}
            </div>
            <div style="flex: 1; min-width: 0;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <div style="font-weight: 600; font-size: 14px;">${this.escapeHtml(displayName)}</div>
                ${unreadBadge}
              </div>
              <div style="font-size: 13px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                ${conv.last_message_sender ? this.escapeHtml(conv.last_message_sender) + ': ' : ''}
                ${this.escapeHtml(lastMessage)}
              </div>
            </div>
          </div>
        `;
      }).join('');
    },

    /**
     * 渲染消息列表
     */
    renderMessages() {
      const container = document.querySelector('[data-messages-container]');
      if (!container) return;

      const messages = this.state.messages[this.state.currentConversationId] || [];

      if (messages.length === 0) {
        container.innerHTML = `
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-muted);">
            <i class="fas fa-comments" style="font-size: 64px; margin-bottom: 16px; opacity: 0.3;"></i>
            <p>开始聊天吧</p>
          </div>
        `;
        return;
      }

      container.innerHTML = messages.map(msg => {
        const isOwn = msg.is_own;
        const timeStr = this.formatTime(msg.created_at);

        return `
          <div class="message ${isOwn ? 'message-own' : 'message-other'}" data-message-id="${msg.id}">
            <div class="message-avatar">
              <img src="${msg.sender_avatar || 'https://via.placeholder.com/40'}"
                   alt="${msg.sender_username}"
                   onerror="this.src='https://via.placeholder.com/40'">
            </div>
            <div class="message-content-wrapper">
              <div class="message-sender">${this.escapeHtml(msg.sender_username)}</div>
              <div class="message-content">${this.escapeHtml(msg.content)}</div>
              <div class="message-time">${timeStr}</div>
            </div>
          </div>
        `;
      }).join('');

      // 滚动到底�?      this.scrollToBottom();
    },

    /**
     * 选择对话
     */
    async selectConversation(conversationId) {
      try {
        this.state.currentConversationId = conversationId;

        // 更新 UI
        document.querySelectorAll('.conversation-item').forEach(item => {
          item.classList.remove('active');
        });
        document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('active');

        // 加载消息
        await this.loadMessages(conversationId);
        this.renderMessages();

        // 标记为已�?        await this.markConversationRead(conversationId);

        // 显示消息输入�?        const inputArea = document.querySelector('[data-message-input-area]');
        if (inputArea) {
          inputArea.style.display = 'flex';
        }

        // 显示聊天区域
        const chatArea = document.querySelector('[data-chat-area]');
        if (chatArea) {
          chatArea.style.display = 'flex';
        }

        // 隐藏空状�?        const emptyState = document.querySelector('[data-empty-state]');
        if (emptyState) {
          emptyState.style.display = 'none';
        }

      } catch (error) {
// console.'选择对话失败:', error);
      }
    },

    /**
     * 发送消息（从输入框�?     */
    async sendFromInput() {
      const input = document.querySelector('[data-message-input]');
      if (!input || !input.value.trim()) return;

      const content = input.value.trim();

      try {
        await this.sendMessage(this.state.currentConversationId, content);
        input.value = '';
      } catch (error) {
        alert('发送失�? ' + error.message);
      }
    },

    /**
     * 更新未读消息徽章
     */
    updateUnreadBadge() {
      const badge = document.querySelector('[data-unread-badge]');
      if (badge) {
        if (this.state.unreadCount > 0) {
          badge.textContent = this.state.unreadCount > 99 ? '99+' : this.state.unreadCount;
          badge.style.display = 'inline-flex';
        } else {
          badge.style.display = 'none';
        }
      }
    },

    /**
     * 滚动到底�?     */
    scrollToBottom() {
      const container = document.querySelector('[data-messages-container]');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },

    /**
     * 获取头像颜色
     */
    getAvatarColor(id) {
      const colors = [
        'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
        'linear-gradient(135deg, #10b981, #34d399)',
        'linear-gradient(135deg, #f59e0b, #fbbf24)',
        'linear-gradient(135deg, #8b5cf6, #a78bfa)',
        'linear-gradient(135deg, #ec4899, #f472b6)',
        'linear-gradient(135deg, #06b6d4, #22d3ee)'
      ];
      return colors[id % colors.length];
    },

    /**
     * 格式化时�?     */
    formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;

      // 小于 1 分钟
      if (diff < 60000) {
        return '刚刚';
      }

      // 小于 1 小时
      if (diff < 3600000) {
        return `${Math.floor(diff / 60000)} 分钟前`;
      }

      // 今天
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      }

      // 昨天
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      }

      // 更早
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + ' ' +
             date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    },

    /**
     * 截断文本
     */
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    },

    /**
     * 显示新建对话模态框
     */
    showNewConversationModal() {
      const modal = document.getElementById('newConversationModal');
      if (modal) {
        modal.classList.add('active');
      }
    },

    /**
     * 隐藏新建对话模态框
     */
    hideNewConversationModal() {
      const modal = document.getElementById('newConversationModal');
      if (modal) {
        modal.classList.remove('active');
        // 清空表单
        document.getElementById('newConversationForm').reset();
      }
    },

    /**
     * 切换对话类型
     */
    toggleConversationType() {
      const type = document.getElementById('conversationType').value;
      const titleGroup = document.getElementById('titleGroup');
      titleGroup.style.display = type === 'group' ? 'block' : 'none';
    },

    /**
     * 创建新对�?     */
    async createNewConversation(event) {
      event.preventDefault();

      const type = document.getElementById('conversationType').value;
      const title = document.getElementById('conversationTitle').value;
      const participantsStr = document.getElementById('participantIds').value;
      const initialMessage = document.getElementById('initialMessage').value;

      // 解析参与�?ID
      const participantIds = participantsStr.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));

      if (participantIds.length === 0) {
        alert('请至少添加一个参与�?);
        return;
      }

      if (type === 'group' && !title) {
        alert('请输入群组名�?);
        return;
      }

      try {
        const result = await this.createConversation(
          type,
          type === 'group' ? title : null,
          participantIds,
          initialMessage || null
        );

        // 如果是新创建的对话，自动选择�?        if (result.created) {
          await this.selectConversation(result.conversation_id);
        } else {
          // 对话已存在，选择�?          await this.selectConversation(result.conversation_id);
        }

        this.hideNewConversationModal();
      } catch (error) {
        alert('创建对话失败: ' + error.message);
      }
    },

    /**
     * 转义 HTML
     */
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  };

  // 导出到全局
  global.MessageAPI = MessageAPI;

  // DOM 加载完成后自动初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (document.querySelector('[data-conversations-list]')) {
        MessageAPI.init();
      }
    });
  } else {
    if (document.querySelector('[data-conversations-list]')) {
      MessageAPI.init();
    }
  }

})(window);
