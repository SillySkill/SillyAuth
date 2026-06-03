/* ============================================
   User Center JS - Profile, Orders, Points, Exchange, Security
   ============================================ */
var UC = {
  API: '/api/v1',
  user: null,
  userId: null,
  isOauthUser: false,
  orderPage: 1, orderLimit: 10,
  pointsPage: 1, pointsLimit: 10,

  /* ---- SHA-256 ---- */
  sha256: (function () {
    var K = [1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298];
    return function (msg) {
      function R(x,n){return(x>>>n)|(x<<(32-n));}
      function S(x,n){return x>>>n;}
      function Ch(x,y,z){return(x&y)^(~x&z);}
      function Maj(x,y,z){return(x&y)^(x&z)^(y&z);}
      function Sigma0(x){return R(x,2)^R(x,13)^R(x,22);}
      function Sigma1(x){return R(x,6)^R(x,11)^R(x,25);}
      function sigma0(x){return R(x,7)^R(x,18)^S(x,3);}
      function sigma1(x){return R(x,17)^R(x,19)^S(x,10);}
      function toBytes(s){var b=[];for(var i=0;i<s.length;i++)b.push(s.charCodeAt(i));return b;}
      var bytes=toBytes(msg);
      var blen=bytes.length*8;
      bytes.push(0x80);
      while((bytes.length%64)!==56)bytes.push(0);
      for(var i=0;i<4;i++)bytes.push(0);
      bytes[bytes.length-1]=blen>>>24&0xff;
      bytes[bytes.length-3]=blen>>>8&0xff;
      bytes[bytes.length-4]=blen&0xff;
      var H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
      for(var c=0;c<bytes.length;c+=64){
        var W=new Array(64);
        for(var t=0;t<16;t++)W[t]=(bytes[c+t*4]<<24)|(bytes[c+t*4+1]<<16)|(bytes[c+t*4+2]<<8)|bytes[c+t*4+3];
        for(t=16;t<64;t++)W[t]=(sigma1(W[t-2])+W[t-7]+sigma0(W[t-15])+W[t-16])>>>0;
        var a=H[0],b=H[1],e=H[2],f=H[3],g=H[4],h=H[5],i=H[6],j=H[7];
        for(t=0;t<64;t++){
          var T1=(j+Sigma1(g)+Ch(g,h,i)+K[t]+W[t])>>>0;
          var T2=(Sigma0(a)+Maj(a,b,e))>>>0;
          j=i;i=h;h=g;g=(f+T1)>>>0;
          f=e;e=b;b=a;a=(T1+T2)>>>0;
        }
        H[0]=(H[0]+a)>>>0;H[1]=(H[1]+b)>>>0;H[2]=(H[2]+e)>>>0;H[3]=(H[3]+f)>>>0;
        H[4]=(H[4]+g)>>>0;H[5]=(H[5]+h)>>>0;H[6]=(H[6]+i)>>>0;H[7]=(H[7]+j)>>>0;
      }
      var hex='';
      for(var k=0;k<8;k++)hex+=((H[k]>>>24)&0xff).toString(16).padStart(2,'0')+((H[k]>>>16)&0xff).toString(16).padStart(2,'0')+((H[k]>>>8)&0xff).toString(16).padStart(2,'0')+(H[k]&0xff).toString(16).padStart(2,'0');
      return hex;
    };
  })(),

  /* ---- Luhn Validation (Client-side, for instant feedback) ---- */
  luhnCheck: function (digits) {
    if (!digits || !/^\d{18}$/.test(digits)) return false;
    var total = 0;
    for (var i = 0; i < 18; i++) {
      var d = parseInt(digits[17 - i], 10);
      if (i % 2 === 1) { d *= 2; if (d > 9) d -= 9; }
      total += d;
    }
    return total % 10 === 0;
  },

  /* ---- Init ---- */
  init: function () {
    this.getToken = (typeof getToken === 'function') ? getToken : function () {
      var m = document.cookie.match(/(?:^|;\s*)access_token=([^;]*)/);
      return m ? m[1] : (localStorage && localStorage.getItem('access_token'));
    };
    this.bindTabs();
    this.bindForms();
    this.loadProfile();
  },

  /* ---- API helpers ---- */
  _token: function () { return this.getToken ? this.getToken() : ''; },

  _api: function (method, path, body) {
    var self = this;
    var headers = { 'Content-Type': 'application/json' };
    var token = self._token();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    var opts = { method: method, headers: headers };
    if (body) opts.body = JSON.stringify(body);
    return fetch(self.API + path, opts).then(function (r) {
      if (!r.ok) return r.json().then(function (e) { throw new Error(e.detail || 'Request failed (' + r.status + ')'); });
      return r.json();
    });
  },
  _get: function (path) { return this._api('GET', path); },
  _put: function (path, body) { return this._api('PUT', path, body); },
  _post: function (path, body) { return this._api('POST', path, body); },

  /* ---- Tabs ---- */
  bindTabs: function () {
    var self = this;
    document.querySelectorAll('.uc-tab').forEach(function (tab) {
      tab.addEventListener('click', function () {
        var target = this.dataset.tab;
        document.querySelectorAll('.uc-tab').forEach(function (t) { t.classList.remove('active'); });
        this.classList.add('active');
        document.querySelectorAll('.uc-panel').forEach(function (p) { p.classList.remove('active'); });
        document.getElementById('panel' + target.charAt(0).toUpperCase() + target.slice(1)).classList.add('active');
        if (target === 'orders') self.loadOrders();
        else if (target === 'points') self.loadPoints();
      });
    });
  },

  /* ---- Forms ---- */
  bindForms: function () {
    var self = this;
    var pf = document.getElementById('profileForm');
    if (pf) pf.addEventListener('submit', function (e) { e.preventDefault(); self.saveProfile(); });
    var sf = document.getElementById('securityForm');
    if (sf) sf.addEventListener('submit', function (e) { e.preventDefault(); self.changePassword(); });
  },

  /* ============== Profile ============== */
  loadProfile: function () {
    var self = this;
    this._get('/auth/me').then(function (data) {
      self.user = data;
      self.userId = data.id;
      self.isOauthUser = data.is_oauth_user || false;
      self._fillProfile(data);
      self._loadStats(data.id);
      self._updateSecurityHint();
    }).catch(function (e) {
      console.warn('loadProfile failed:', e);
      var nameEl = document.getElementById('profileName');
      if (nameEl && nameEl.textContent && nameEl.textContent !== '用户') {
        self.userId = self.userId || 1;
        self._loadStats(self.userId);
      }
    });
  },

  _fillProfile: function (data) {
    var d = data || {};
    var displayName = d.first_name || d.username || '';
    var username = d.username || '';

    // Profile card
    document.getElementById('profileName').textContent = displayName || username || '用户';
    document.getElementById('profileEmail').textContent = d.email || '';
    document.getElementById('profileAvatar').textContent = (username || d.email || 'U').charAt(0).toUpperCase();

    // Form fields
    var u = document.getElementById('editUsername'); if (u) u.value = username;
    var e = document.getElementById('editEmail'); if (e) e.value = d.email || '';
    var dn = document.getElementById('editDisplayName'); if (dn) dn.value = displayName;
    var ph = document.getElementById('editPhone'); if (ph) ph.value = d.phone || '';
    var bio = document.getElementById('editBio'); if (bio) bio.value = d.bio || '';
  },

  _loadStats: function (uid) {
    var self = this;
    this._get('/store/orders?user_id=' + (uid || self.userId) + '&limit=1&offset=0').then(function (d) {
      document.getElementById('statOrders').textContent = Array.isArray(d) ? d.length : (d.total || 0);
    }).catch(function () { document.getElementById('statOrders').textContent = '0'; });
    this._get('/points/balance?user_id=' + (uid || self.userId)).then(function (d) {
      document.getElementById('statPoints').textContent = d.balance || 0;
      document.getElementById('statLevel').textContent = d.level || 1;
    }).catch(function () {
      document.getElementById('statPoints').textContent = '0';
      document.getElementById('statLevel').textContent = '1';
    });
  },

  saveProfile: function () {
    var self = this;
    var btn = document.querySelector('#profileForm button[type=submit]');
    btn.disabled = true; btn.textContent = '保存中...';
    this._clearMsg('profileMsg');
    var body = {
      username: document.getElementById('editUsername').value.trim(),
      email: document.getElementById('editEmail').value.trim(),
      first_name: document.getElementById('editDisplayName').value.trim(),
      phone: document.getElementById('editPhone').value.trim(),
      bio: document.getElementById('editBio').value.trim()
    };
    this._put('/auth/me', body).then(function (data) {
      self.user = data;
      self._fillProfile(data);
      self._showMsg('profileMsg', 'success', '资料保存成功');
      btn.disabled = false; btn.textContent = '保存';
    }).catch(function (e) {
      self._showMsg('profileMsg', 'error', e.message);
      btn.disabled = false; btn.textContent = '保存';
    });
  },

  /* ============== Orders ============== */
  loadOrders: function () {
    var self = this;
    if (!self.userId) return;
    var status = document.getElementById('orderStatusFilter').value;
    var params = 'user_id=' + self.userId + '&limit=' + self.orderLimit + '&offset=' + ((self.orderPage - 1) * self.orderLimit);
    if (status) params += '&status=' + status;
    var tbody = document.getElementById('orderListBody');
    tbody.innerHTML = '<tr class=\"loading-row\"><td colspan=\"6\"><span class=\"spinner-inline\"></span>加载中...</td></tr>';
    this._get('/store/orders?' + params).then(function (data) {
      var orders = Array.isArray(data) ? data : (data.items || []);
      self._renderOrders(orders);
    }).catch(function (e) {
      tbody.innerHTML = '<tr class=\"loading-row\"><td colspan=\"6\">加载失败: ' + (e.message || '网络错误') + '</td></tr>';
    });
  },

  _renderOrders: function (orders) {
    var self = this, tbody = document.getElementById('orderListBody');
    if (!orders || orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan=\"6\"><div class=\"empty-state\"><i class=\"fas fa-shopping-bag\"></i><p>暂无订单记录</p></div></td></tr>';
      document.getElementById('orderPagination').innerHTML = '';
      return;
    }
    var sm = { pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消' };
    tbody.innerHTML = orders.map(function (o) {
      var st = o.status || '';
      return '<tr>' +
        '<td class=\"order-no\">' + (o.order_no || '') + '</td>' +
        '<td>' + (o.product_name || o.description || '商品') + '</td>' +
        '<td class=\"order-amount\">' + (o.total_amount != null ? '¥' + Number(o.total_amount).toFixed(2) : '-') + '</td>' +
        '<td><span class=\"status status-' + (st || 'pending') + '\">' + (sm[st] || st || '未知') + '</span></td>' +
        '<td>' + (o.created_at ? o.created_at.substring(0, 10) : '-') + '</td>' +
        '<td><button class=\"uc-btn uc-btn-outline uc-btn-sm\" onclick=\"UC.viewOrder(\'' + (o.order_no || '') + '\')\">详情</button></td>' +
        '</tr>';
    }).join('');
    document.getElementById('orderPagination').innerHTML =
      '<button ' + (self.orderPage <= 1 ? 'disabled' : '') + ' onclick=\"UC.orderPage--;UC.loadOrders()\">上一页</button>' +
      '<span class=\"page-current\">第 ' + self.orderPage + ' 页</span>' +
      '<button onclick=\"UC.orderPage++;UC.loadOrders()\">下一页</button>';
  },

  viewOrder: function (no) { window.location.href = '/sillyfu/order/' + no; },

  /* ============== Points ============== */
  loadPoints: function () { this.loadBalance(); this.loadTransactions(); },

  loadBalance: function () {
    var self = this;
    if (!self.userId) return;
    this._get('/points/balance?user_id=' + self.userId).then(function (d) {
      document.getElementById('balanceValue').textContent = d.balance || 0;
      document.getElementById('statPoints').textContent = d.balance || 0;
    }).catch(function () { document.getElementById('balanceValue').textContent = '0'; });
  },

  loadTransactions: function () {
    var self = this;
    if (!self.userId) return;
    var tbody = document.getElementById('pointsTxnBody');
    tbody.innerHTML = '<tr class=\"loading-row\"><td colspan=\"5\"><span class=\"spinner-inline\"></span>加载中...</td></tr>';
    this._get('/points/transactions?user_id=' + self.userId + '&page=' + self.pointsPage + '&page_size=' + self.pointsLimit).then(function (data) {
      self._renderTxns(data.items || data.transactions || []);
    }).catch(function () {
      self._get('/points/history?user_id=' + self.userId + '&page=' + self.pointsPage + '&limit=' + self.pointsLimit).then(function (data) {
        self._renderTxns(data.items || data.transactions || []);
      }).catch(function () {
        tbody.innerHTML = '<tr><td colspan=\"5\"><div class=\"empty-state\"><i class=\"fas fa-history\"></i><p>暂无积分记录</p></div></td></tr>';
        document.getElementById('pointsPagination').innerHTML = '';
      });
    });
  },

  _renderTxns: function (items) {
    var self = this, tbody = document.getElementById('pointsTxnBody');
    if (!items || items.length === 0) {
      tbody.innerHTML = '<tr><td colspan=\"5\"><div class=\"empty-state\"><i class=\"fas fa-history\"></i><p>暂无积分记录</p></div></td></tr>';
      document.getElementById('pointsPagination').innerHTML = '';
      return;
    }
    var tm = { earn: '收入', spend: '支出', recharge: '充值', sign_in: '签到', exchange: '兑换', purchase: '购物', admin: '系统', redeem_serial: '兑换码' };
    tbody.innerHTML = items.map(function (t) {
      var amt = t.amount || t.points || 0, isEarn = amt >= 0, tn = t.transaction_type || t.type || '';
      return '<tr>' +
        '<td>' + (t.created_at ? t.created_at.substring(0, 16) : '-') + '</td>' +
        '<td class=\"txn-type\">' + (tm[tn] || tn || '积分变动') + '</td>' +
        '<td>' + (t.description || t.note || '-') + '</td>' +
        '<td class=\"' + (isEarn ? 'txn-earn' : 'txn-spend') + '\">' + (isEarn ? '+' : '') + amt + '</td>' +
        '<td>' + (t.balance_after != null ? t.balance_after : (t.balance_before != null ? t.balance_before : '-')) + '</td>' +
        '</tr>';
    }).join('');
    document.getElementById('pointsPagination').innerHTML =
      '<button ' + (self.pointsPage <= 1 ? 'disabled' : '') + ' onclick=\"UC.pointsPage--;UC.loadTransactions()\">上一页</button>' +
      '<span class=\"page-current\">第 ' + self.pointsPage + ' 页</span>' +
      '<button onclick=\"UC.pointsPage++;UC.loadTransactions()\">下一页</button>';
  },

  showRecharge: function () {
    var card = document.getElementById('rechargeCard');
    card.style.display = card.style.display === 'none' ? 'block' : 'none';
  },

  doRecharge: function () {
    var self = this, amt = parseInt(document.getElementById('rechargeAmount').value);
    if (!amt || amt < 1) { this._showMsg('rechargeMsg', 'error', '请输入有效的充值金额'); return; }
    var btn = document.querySelector('#rechargeCard .uc-btn-primary');
    if (btn) { btn.disabled = true; btn.textContent = '处理中...'; }
    this._clearMsg('rechargeMsg');
    this._post('/points/recharge?user_id=' + self.userId + '&amount=' + amt).then(function () {
      self._showMsg('rechargeMsg', 'success', '成功充值 ' + amt + ' 积分');
      document.getElementById('rechargeAmount').value = '';
      self.loadBalance(); self.loadTransactions();
      if (btn) { btn.disabled = false; btn.textContent = '确认充值'; }
    }).catch(function (e) {
      self._showMsg('rechargeMsg', 'error', '充值失败: ' + (e.message || '请稍后重试'));
      if (btn) { btn.disabled = false; btn.textContent = '确认充值'; }
    });
  },

  /* ============== Serial Exchange (积分兑换) ============== */
  doExchange: function () {
    var self = this;
    var input = document.getElementById('serialInput');
    var serial = input.value.replace(/\s/g, '');
    self._clearMsg('exchangeMsg');
    var resultEl = document.getElementById('exchangeResult');
    if (resultEl) { resultEl.style.display = 'none'; resultEl.innerHTML = ''; }

    // Validate format
    if (!serial || serial.length !== 18) {
      self._showMsg('exchangeMsg', 'error', '请输入18位兑换码');
      return;
    }
    if (!/^\d{18}$/.test(serial)) {
      self._showMsg('exchangeMsg', 'error', '兑换码只能包含数字');
      return;
    }

    // Client-side Luhn check for instant feedback
    if (!self.luhnCheck(serial)) {
      self._showMsg('exchangeMsg', 'error', '兑换码校验失败，请检查是否正确');
      return;
    }

    var btn = document.querySelector('#panelPoints .uc-card:nth-child(3) .uc-btn-primary');
    if (btn) { btn.disabled = true; btn.textContent = '兑换中...'; }

    this._post('/points/exchange-serial', { serial_number: serial, user_id: self.userId }).then(function (data) {
      if (resultEl) {
        resultEl.style.display = 'block';
        resultEl.className = 'exchange-result success';
        var info = data.product_info || {};
        resultEl.innerHTML =
          '<p><strong>' + data.message + '</strong></p>' +
          '<div class=\"exchange-detail\">' +
          (info.capacity ? '<span>容量: ' + info.capacity + '</span>' : '') +
          (info.color ? '<span>颜色: ' + info.color + '</span>' : '') +
          (info.date ? '<span>生产日期: ' + info.date + '</span>' : '') +
          (info.batch ? '<span>批次: ' + info.batch + '</span>' : '') +
          '</div>' +
          '<p class=\"exchange-balance\">当前余额: <strong>' + data.current_balance + '</strong> 积分</p>';
      }
      input.value = '';
      self.loadBalance(); self.loadTransactions();
      self._showMsg('exchangeMsg', 'success', data.message);
      if (btn) { btn.disabled = false; btn.textContent = '兑换'; }
    }).catch(function (e) {
      self._showMsg('exchangeMsg', 'error', '兑换失败: ' + (e.message || '请稍后重试'));
      if (btn) { btn.disabled = false; btn.textContent = '兑换'; }
    });
  },

  /* ============== Security ============== */
  _updateSecurityHint: function () {
    var hint = document.getElementById('securityOauthHint');
    var oldPwdField = document.getElementById('oldPasswordField');
    var oldPwdInput = document.getElementById('oldPassword');
    if (this.isOauthUser) {
      if (hint) hint.style.display = 'block';
      if (oldPwdField) oldPwdField.style.display = 'none';
      if (oldPwdInput) { oldPwdInput.required = false; oldPwdInput.value = ''; }
    } else {
      if (hint) hint.style.display = 'none';
      if (oldPwdField) oldPwdField.style.display = '';
      if (oldPwdInput) oldPwdInput.required = true;
    }
  },

  changePassword: function () {
    var self = this;
    var oldPwd = document.getElementById('oldPassword').value;
    var newPwd = document.getElementById('newPassword').value;
    var confirmPwd = document.getElementById('confirmPassword').value;
    self._clearMsg('securityMsg');

    if (!newPwd || !confirmPwd) { self._showMsg('securityMsg', 'error', '请填写所有密码字段'); return; }

    // For WeChat OAuth users, old password is optional
    if (!self.isOauthUser) {
      if (!oldPwd) { self._showMsg('securityMsg', 'error', '请输入当前密码'); return; }
    }

    if (newPwd !== confirmPwd) { self._showMsg('securityMsg', 'error', '两次输入的新密码不一致'); return; }
    if (newPwd.length < 6) { self._showMsg('securityMsg', 'error', '新密码至少需要6位'); return; }

    // Hash with SHA-256
    var hashOld = self.isOauthUser && !oldPwd ? '' : self.sha256(oldPwd);
    var hashNew = self.sha256(newPwd);

    var btn = document.querySelector('#securityForm button[type=submit]');
    if (btn) { btn.disabled = true; btn.textContent = '更新中...'; }

    this._post('/auth/change-password', { old_password: hashOld, new_password: hashNew }).then(function () {
      self._showMsg('securityMsg', 'success', '密码修改成功');
      document.getElementById('oldPassword').value = '';
      document.getElementById('newPassword').value = '';
      document.getElementById('confirmPassword').value = '';
      if (btn) { btn.disabled = false; btn.textContent = '更新密码'; }
    }).catch(function (e) {
      self._showMsg('securityMsg', 'error', '修改失败: ' + (e.message || '密码错误'));
      if (btn) { btn.disabled = false; btn.textContent = '更新密码'; }
    });
  },

  /* ============== Logout ============== */
  logout: function () {
    if (!confirm('确定退出当前账号？')) return;
    var self = this;
    this._post('/auth/logout', {}).then(function () {
      self._clearAuth();
    }).catch(function () {
      self._clearAuth();
    });
  },
  _clearAuth: function () {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    document.cookie = 'access_token=; path=/; max-age=0';
    document.cookie = 'refresh_token=; path=/; max-age=0';
    window.location.href = '/';
  },

  /* ---- Utils ---- */
  _showMsg: function (id, type, msg) {
    var el = document.getElementById(id);
    if (!el) return;
    el.className = 'uc-msg ' + type; el.textContent = msg;
  },
  _clearMsg: function (id) {
    var el = document.getElementById(id);
    if (el) { el.className = 'uc-msg'; el.textContent = ''; }
  }
};

document.addEventListener('DOMContentLoaded', function () { UC.init(); });
