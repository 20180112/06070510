# K8s / Linux / Docker 细分讲义（云原生 AI 平台）

给「没运维过集群、Linux 不熟」用。每节先人话，再命令，再面试怎么说。  
岗位口径、自我介绍、训练/推理题仍看 [`云原生AI平台面试准备.md`](云原生AI平台面试准备.md)。

建议顺序：A1–A3（文件、进程、`nvidia-smi`）→ B（镜像 vs 容器）→ C2、C3、C5、C6（Pod/Job/kubectl/GPU Pending）→ C8、C10（PVC 和 YAML）→ A6 操作系统口述。没环境也可以先背概念；有一台云主机或自己电脑装 Docker 更好。不要装生产运维经验。

---

## A. Linux：你日常会碰到的操作

训练平台最后还是 Linux 进程 + 文件 + 网络。下面按「排障顺序」学。

### A1. 文件和目录

一切都是文件。重要路径：

| 路径 | 是什么 |
| --- | --- |
| `/` | 根目录 |
| `/home/你的用户名` | 家目录，`~` |
| `/tmp` | 临时文件，重启可能清 |
| `/var/log` | 日志 |
| `/dev` | 设备（磁盘、GPU 在系统里也有设备节点） |

常用命令（要能说干什么，不必全记住参数）：

```bash
pwd                  # 我在哪
ls -l                # 列表，含权限
cd /path             # 进目录
mkdir -p a/b         # 建目录
cp -r src dst        # 复制
mv a b               # 改名或移动
rm -rf dir           # 删除（面试别吹乱删）
cat file             # 打印全文
less file            # 翻页看
head -n 50 file      # 前 50 行
tail -n 50 file      # 后 50 行，训练日志常用
tail -f log.txt      # 一直盯着新增日志
grep "Error" log     # 搜索
find . -name "*.ckpt"
du -sh *             # 各目录占多少盘
df -h                # 磁盘满没
```

权限 `ls -l` 看到 `rwxr-xr-x`：所有者/组/其他人的读、写、执行。  
`chmod +x run.sh` 让脚本能执行。  
`chown user:group file` 改所有者。训练任务写不了 ckpt，经常是权限或盘满。

口头：「日志用 tail 和 grep；磁盘用 df；程序起不来先看权限和路径。」

### A2. 进程

进程 = 正在跑的程序。训练就是一个（或一组）Python 进程。

```bash
ps aux | grep python    # 谁在跑
top / htop              # CPU、内存实时
kill PID                # 结束进程
kill -9 PID             # 强制（最后手段）
nvidia-smi              # GPU 谁占用、显存多少
```

前台：命令占着终端。  
后台：`python train.py &` 或 `nohup python train.py > out.log 2>&1 &`  
`2>&1`：错误输出也进同一个日志。平台上这些由容器和日志系统代劳，但面试要懂「进程 + 标准输出」。

**进程 vs 线程：** 进程有独立内存；线程共享内存。DataLoader 的 `num_workers` 是多进程拉数据。  
**CPU 高、GPU 低：** 常是数据预处理慢，GPU 在等。

口头：「nvidia-smi 看卡和进程；利用率低先分是 GPU 算得慢还是 CPU 喂不进数据。」

### A3. 环境变量与 Python 环境

```bash
echo $PATH
export CUDA_VISIBLE_DEVICES=0,1   # 只让程序看见这两张卡
which python
pip list
```

平台用镜像固定 Python/CUDA，就是避免「我机器能跑、集群缺库」。  
`CUDA_VISIBLE_DEVICES` 是调度时常用的：Pod 里只暴露申请到的卡。

### A4. 网络（排障用）

```bash
ping 8.8.8.8
curl -I http://localhost:8000     # 推理服务通不通
ss -lntp                          # 谁在听端口（或 netstat）
```

本机 `127.0.0.1`，容器之间用 Service 名。端口没开、防火墙、服务没起来，都会连不上。

TCP：要握手、可靠，训练梯度、HTTP 推理都用它。  
UDP：不保证到达，一般不是训练主路径。

### A5. 用户、管道、重定向

```bash
whoami
sudo 某命令              # 用管理员（容器里常常没有 sudo）
python train.py > out.txt           # 标准输出进文件
python train.py > out.txt 2>&1      # 包含报错
cat log | grep Exception
```

### A6. 校招常问的操作系统概念（人话版）

这些不是让你写内核，是让你能把「训练为什么卡、为什么 OOM」说圆。

**进程 vs 线程**  
进程：独立地址空间，互相基本看不见内存。  
线程：同一进程里共享内存。PyTorch DataLoader 的 `num_workers` 是**多进程**拉数据，避免被 Python GIL 卡住。训练主进程再把 tensor 拷到 GPU。

**用户态 / 内核态**  
你写的 Python 在用户态跑。读磁盘、发网络、申请内存，要进内核。所以「代码看起来在算，实际在等 IO」很常见。

**虚拟内存 / OOM**  
进程以为有一块连续大内存，其实是内核映射过去的。物理内存不够就用交换分区（swap，训练时很慢）或直接杀进程（OOM Killer）。GPU OOM 是显存不够，和主机内存 OOM 是两件事：`nvidia-smi` 看前者，`dmesg` / `free -h` 看后者。

**文件描述符 fd**  
打开的文件、socket、管道在进程里都是一个整数编号。`ulimit -n` 太小，训练同时开很多数据文件会报 `Too many open files`。

**管道和重定向（再记一句）**  
`|` 把前一个命令的输出送给后一个。`>` 写文件。`2>&1` 把报错也并进同一个文件。平台采集的「训练日志」本质就是容器的 stdout/stderr。

口头：「GPU 训练仍要很多 CPU，是因为 DataLoader 在 CPU 上解码、增强、组 batch；卡利用率低先分是算得慢还是喂数慢。」

### A7. 容器为什么能隔离（和内核的关系，加分口述）

Linux **namespace**：每个容器有自己的进程树、网络、挂载，看不见别人的进程。  
**cgroup：** 限制 CPU、内存、（加上插件后）GPU 用量，防止一个训练把节点吃光。  
Docker/K8s 都是调这两套，不是另一套操作系统。  
JD「熟悉 Linux 内核」到这一句就够，不要说改过调度器。

---

## B. Docker：镜像和容器

**镜像 image：** 只读模板（Ubuntu + CUDA + Python + 你的代码依赖）。  
**容器 container：** 镜像跑起来的进程 + 可写层。训练 Job = 起一个容器跑 `python train.py`。

类比：镜像是安装盘，容器是装好正在跑的电脑。

```bash
docker build -t mytrain:v1 .      # 按 Dockerfile 打镜像
docker images
docker run --gpus all -v /data:/data mytrain:v1 python train.py
docker ps                         # 正在跑
docker logs -f 容器ID
docker exec -it 容器ID bash       # 进容器里看
docker stop 容器ID
```

`-v 宿主机路径:容器路径`：把数据盘挂进去，否则容器删了 ckpt 没了。  
端口 `-p 8000:8000`：推理服务用。

Dockerfile 最小印象：

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
RUN pip install torch ...
COPY . /app
WORKDIR /app
CMD ["python", "train.py"]
```

`FROM` 必须带匹配的 CUDA，否则 GPU 驱动对不上。  
口头：「本地 conda 能跑不等于集群能跑；平台要的是同一份镜像。」

---

## C. Kubernetes 细分

### C1. 集群长什么样

- **Control plane（控制面）：** 大脑。调度、存集群状态（etcd）、API（你敲的 kubectl 打到这）。  
- **Node（工作节点）：** 真正跑容器的机器，上面有 kubelet。GPU 机器就是带 GPU 的 Node。  
- 你不直接 ssh 到每台机器上起 Python，而是告诉 API：「我要一个 Pod」。

### C2. Pod 是最小单位

Pod = 一台「小机器」：共享网络和磁盘的一组容器（训练通常就一个主容器）。  
有自己的 IP，但会变，所以前面再挂 Service。

一个训练 Pod 里典型有：

- 镜像（含 PyTorch）  
- 命令 `python train.py --lr ...`  
- 资源：`cpu: 8`，`memory: 32Gi`，`nvidia.com/gpu: 4`  
- 挂载：数据 PVC、输出 PVC  
- 环境变量：`NCCL_...`、`WANDB_...`

Pod 生命周期：Pending（还没分到节点）→ Running → Succeeded / Failed。

### C3. 为什么还有 Deployment、Job、Service

| 种类 | 干什么 | AI 平台何时用 |
| --- | --- | --- |
| **Pod** | 最小运行单位 | 底层都是 Pod |
| **Job** | 跑完退出，失败可重试 N 次 | **训练、离线评测** |
| **Deployment** | 保持 N 副本一直在，挂了拉起来 | **在线推理** |
| **Service** | 稳定域名/端口，转到后端 Pod | 推理入口、训练中间件 |
| **CronJob** | 定时 Job | 定期扫数据、清理 |

口头：「训练用 Job，因为有始有终；推理用 Deployment，因为要一直服务。」

### C4. 名字空间、标签

**Namespace：** 逻辑隔离（团队 A / 团队 B），不是物理机隔离。  
**Label：** `app=infer, model=qwen` 键值对，Service 靠它选中哪些 Pod。

### C5. 你真正会敲的 kubectl（背这几条）

```bash
kubectl get nodes
kubectl get pods -n 命名空间
kubectl describe pod 名字          # 为什么 Pending、事件
kubectl logs -f pod名字            # 看训练输出
kubectl exec -it pod名字 -- bash   # 进去 nvidia-smi
kubectl apply -f job.yaml          # 提交
kubectl delete job 名字
```

`describe` 里 **Events** 最重要：FailedScheduling、Insufficient nvidia.com/gpu、镜像拉取失败。

### C6. 调度和 GPU

默认调度器看：节点还剩多少 CPU/内存/GPU，污点 taint、亲和度。  
GPU：节点装 NVIDIA Device Plugin，于是资源名多了 `nvidia.com/gpu`。  
申请 8 卡但 Pending：

1. 没有节点剩 8 张空闲卡（碎片：两台各 4 张空闲凑不齐，要看是否允许跨机 DDP）  
2. 卡型号不对（要 A100 只有 V100）  
3. 配额 Quota 用完  
4. 镜像太大一直 Pulling  
5. 声明了不存在的 PVC

跨机 8 卡 = 多个 Pod 组成一个训练 Job（PyTorchJob / MPIJob），还要网络打通 NCCL。

### C7. 配置和密钥

**ConfigMap：** 非机密配置（超参、路径）。  
**Secret：** 密码、访问密钥，挂成环境变量或文件。  
别把 AK/SK 写进镜像。

### C8. 存储 PVC（一定要懂）

Pod 默认磁盘是临时的，删 Pod 数据没。  
**PVC（PersistentVolumeClaim）：** 「我要 2T 读写」。集群用 **PV** 对接 NAS/云盘/RBD。

多机训练同时读同一份 ImageNet：用 **ReadWriteMany** 的 NAS。  
OSS：对象存储，适合备份 ckpt，直接随机读小文件可能慢，常先缓存。

口头：「数据盘用 PVC 挂 NAS；归档 ckpt 可以定期传到 OSS。」

### C9. 健康检查（推理 Deployment）

- **liveness：** 探活失败就重启容器（死锁有用，训练 Job 一般慎用，怕训到一半被杀）。  
- **readiness：** 没准备好不要接流量（模型还在加载）。

### C10. YAML 不必默写全文，要能看懂字段

脑子里有这些键：`apiVersion, kind, metadata, spec, containers, resources, volumeMounts`。  
面试说：「我能看懂 Job 的镜像、命令、GPU 数量和挂盘；没写过复杂 Operator。」

对照读这一份就够（注释不要真写进集群 YAML）：

```yaml
apiVersion: batch/v1
kind: Job                          # 跑完退出，适合训练
metadata:
  name: train-watermark
  namespace: research              # 逻辑隔离，不是一台机器
spec:
  backoffLimit: 2                  # 失败最多再试 2 次
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: trainer
        image: registry/train:v1   # 含 CUDA + PyTorch
        command: ["python", "train.py"]
        args: ["--lr", "1e-4"]
        resources:
          limits:
            nvidia.com/gpu: 4      # 向 Device Plugin 要 4 张卡
            cpu: "8"
            memory: 32Gi
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0,1,2,3"         # 常见由平台注入，不必手写
        volumeMounts:
        - name: data
          mountPath: /mnt/data     # 容器内路径
        - name: output
          mountPath: /mnt/output
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: imagenet-nas  # 对应一块 PVC
      - name: output
        persistentVolumeClaim:
          claimName: ckpt-pvc
```

看 YAML 时按这个顺序：`kind` → 镜像和命令 → `nvidia.com/gpu` → 挂了哪几块盘 → 失败重试。

### C11. 和 Linux 命令怎么对上号

| 你在单机上做的事 | 在集群里对应 |
| --- | --- |
| `python train.py` | Job 的 `command` |
| `nvidia-smi` | `kubectl exec` 进 Pod 再敲，或看平台监控 |
| `tail -f log` | `kubectl logs -f` |
| `df -h` / 盘满 | PVC 容量、节点磁盘、`df` 在容器里 |
| `export CUDA_VISIBLE_DEVICES` | Pod 资源声明 + 运行时注入 |
| `docker run -v ...` | `volumeMounts` + PVC |

---

## D. 和训练任务串起来（一条故事）

你在平台点「提交训练」时，背后大致是：

1. 平台生成一份 Job YAML（镜像=你的训练镜像，GPU=4，命令=python train.py）。  
2. Argo 或 Kubeflow 可能先跑「下载数据」再跑训练。  
3. kube-scheduler 找有 4 张空卡的节点。  
4. kubelet 拉镜像、挂 PVC、起容器。  
5. 容器里 `CUDA_VISIBLE_DEVICES` 已是 0-3，你的 PyTorch DDP 开跑。  
6. stdout 被采集成 `kubectl logs`；ckpt 写到 `/mnt/output`（NAS）。  
7. 进程退出码 0 → Job Succeeded；非 0 → 按 restartPolicy 重试。

你能讲这条链，就说明 K8s 不是背单词。

---

## E. Kubeflow / Argo（各记一个定位）

**Argo Workflow：** 多步骤流水线。每步是一个模板（容器）。边表示先后。失败重试、超时。适合：准备数据 → 训练 → 评测 → 导出模型。

**Kubeflow：** 在 K8s 上给 ML 用的一整套（Notebook、Pipeline、训练 Operator）。PyTorchJob 会帮你拉起多 Pod 做 DDP，而不用自己写 8 个 Pod YAML。

没搭过：定位说对，别讲安装细节。

---

## F. 建议动手（有时间）

1. 本机或云主机：`docker run hello-world`，再跑一个 `python:3.10` 进去 `ls`。  
2. 若有 Minikube/K3s：`kubectl run` 一个 nginx，`get pods`，`logs`。  
3. 没有集群：把上面 kubectl 五条和 Pending 五种原因背熟，比装环境优先级更高。

---

## G. 口头自测

1. `df -h` 和 `du -sh` 差别？  
2. 为什么训练容器要 `-v` 或 PVC？  
3. Job 和 Deployment 各举一个 AI 例子。  
4. describe pod 看哪一段判断 Pending？  
5. namespace 和 node 是一层东西吗？  
6. cgroup 解决什么问题？  
7. OSS 和 NAS 训练读数据哪个更合适？为什么？  
8. GPU OOM 和主机 OOM 分别看什么？  
9. 为什么 YAML 里写 `nvidia.com/gpu: 4`，容器里还是看到 0,1,2,3？

答案要点：1）df 看盘还剩多少，du 看目录多大。2）容器删了临时盘没了。3）训练 Job，推理 Deployment。4）Events。5）不是，ns 是逻辑，node 是机器。6）限制资源。7）多机共读常用 NAS；OSS 适合存归档，直接训练可能慢。8）前者 `nvidia-smi`，后者 `free -h` / 内核杀进程。9）Device Plugin 把节点上的卡映射进 Pod，容器内编号从 0 起算，不一定等于整机物理编号。
