#!/usr/bin/env python
# coding:utf-8
import os,sys
if sys.argv[1]:
    hostname=sys.argv[1]
else:
    hostname=os.popen('hostname').read()

from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY


class EventHandler(ProcessEvent):
    def process_IN_CREATE(self, event):
        print "创建文件:%s." % os.path.join(event.path, event.name)
        mail('主机:%s有文件被创建,被创建的文件名:%s'%(hostname,os.path.join(event.path, event.name)), '文件监控告警')
        # os.system('cp -rf %s /tmp/bak/'%(os.path.join(event.path,event.name)))

    def process_IN_DELETE(self, event):
        print "删除文件:%s." % os.path.join(event.path, event.name)
        mail('主机:%s有文件被删除,被删除的文件名:%s'%(hostname,os.path.join(event.path, event.name)), '文件监控告警')

    def process_IN_MODIFY(self, event):
        print "修改文件:%s." % os.path.join(event.path, event.name)
        mail('主机:%s有文件被修改,被修改的文件名:%s'%(hostname,os.path.join(event.path, event.name)), '文件监控告警')


def FsMonitor(path='.'):
    wm = WatchManager()
    mask = IN_DELETE | IN_CREATE | IN_MODIFY
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, auto_add=True, rec=True)
    print "现在开始监视 %s." % path

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                print "检查事件是否正确."
                notifier.read_events()
        except KeyboardInterrupt:
            print "键盘中断."
            notifier.stop()
            break


def mail(info, mailtitle):
    from email import encoders
    from email.header import Header
    from email.mime.text import MIMEText
    from email.utils import parseaddr, formataddr

    import smtplib

    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    from_addr = 'xxxx@xxxx.cn'#SMTP账号
    password = 'xxxxxH'#SMTP密码
    to_addr = 'jiangwh@healthmall.cn'#邮件接收人
    smtp_server = 'smtp.mxhichina.com'#SMTP服务器地址

    msg = MIMEText(info, 'plain', 'utf-8')
    msg['From'] = _format_addr('系统提示 <%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header(mailtitle, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


if __name__ == "__main__":
    if sys.argv[2]:
        dirname=sys.argv[2]
    else:
        dirname='/'
    FsMonitor(dirname)
