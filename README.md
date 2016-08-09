# check_codis_dashboard
检测redis集群服务codis的dashboard状态

工作中使用codis做为redis集群，dashboard是codis重要的组件。

生产环境中发现dashboard经常挂掉，虽然不影响集群的正常使用，但是感觉很是不爽。

因此写了个检测脚本，虽然无法彻底解决dashboard挂掉的问题，但是可以节省运维操作。

check_codis_dashboard.go 尚不完备，无法使用

check_codis_dashboard.py 可以被使用
