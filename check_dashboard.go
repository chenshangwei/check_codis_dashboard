/*
* 检测codis中的dashboard进程
*     如果该进程挂掉，则重启它
*         因为zookeeper的缘故，在重启之前需要将zk中的dashboard信息delete掉
*
* 使用前，
*     配置zk连接信息与dashboard命令
*     你可能需要执行 go get github.com/samuel/go-zookeeper/zk
* github.com/chenshangwei/check_codis_dashboard
*/

package main

import (
   "fmt"
   "time"
   "log"
   "os"
   "os/exec"
   "net/http"
   s "strings"
   "github.com/samuel/go-zookeeper/zk"
)

/*config*/
var zk_ip  = []string{"192.168.1.200"}
var addr string = "192.168.1.200:18087"
var zk_dashboard = "/zk/codis/db_120ask/dashboard"
var dashboard_command string = "/home/go/src/github.com/CodisLabs/codis/bin/codis-config"
var dashboard_args string = "-c /home/go/src/github.com/CodisLabs/codis/config.ini -L /home/go/src/github.com/CodisLabs/codis/logs/dashboard.log dashboard --addr "+addr  //最后不加&
var logFile string = "/root/tools/check_dashboard.log"


//http请求，判断dashboard是否存活
func check() bool{
   url := "http://"+addr+"/api/overview"
   //url := "http://www.baidu.com"
   if resp,err := http.Get(url);err != nil {
      return false
   } else {
      resp.Body.Close()
      return true
   }
}
//记录日志
func writeLog(msg string){
   logfile,err := os.OpenFile(logFile,os.O_RDWR|os.O_CREATE|os.O_APPEND,0666);
   if err!=nil {
      panic(err)
   }
   defer logfile.Close();
   logger := log.New(logfile,"\r\n",log.Ldate|log.Ltime|log.Llongfile);
   logger.Fatal(msg);
}
//启动dashboard
func runDashboard(){
   fmt.Println("exec : " + dashboard_command)
   var argArray []string
   argArray = s.Split(dashboard_args," ")
   
   cmd := exec.Command(dashboard_command,argArray...)
   if err := cmd.Start();err != nil {
      writeLog("[fail]start dashboard")
   }else{
      writeLog("[success]start dashboard")
   }
}
//删掉zk中的dashboard信息
func delDashboard() {
   fmt.Println("delete : " + zk_dashboard)
   if c,_, err := zk.Connect(zk_ip, time.Second*2);err != nil {
      writeLog("[fail]connect zk")
   }else{
      d,_,_ := c.Get(zk_dashboard)
      fmt.Printf("%s",d)
      if len(d)>0 {
         err := c.Delete(zk_dashboard,-1)
         if err != nil {
            writeLog("[fail]delete zk_dashboard")
         }else{
            writeLog("[success]delete zk_dashboard")
         }
      }
   }
}
func main() {
   if check() {
      fmt.Println("zk dashboard is ok")
      //os.Exit(0)
   }
   delDashboard()
   runDashboard()
}
