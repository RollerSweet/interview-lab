## Linux Container

Understand what a Linux container really is (namespaces + cgroups + a root filesystem) and practice building one manually without Docker.

### 1. What Is a Container?
- **Namespaces**: isolate process views (PID, network, mount, UTS hostname, IPC, user IDs). A containerized process thinks it is alone because these namespaces hide the host.
- **Control Groups (cgroups)**: enforce resource limits and accounting for CPU, memory, IO.
- **Root filesystem**: directory tree the process uses as `/`. Using `chroot` or overlayfs lets you provide minimal rootfs images.
- **Runtime**: `runc`, `containerd`, Docker, etc., are conveniences that configure these primitives for you, but the kernel features exist independently.

In this lab we manually enter new namespaces and optionally mount a minimal root filesystem to see the building blocks in action.

### 2. Create a Container-Like Shell with `unshare`
`unshare` lets you create new namespaces from the command line. Run:
```bash
sudo unshare --mount --uts --ipc --pid --net --fork --user --map-root-user bash
```

Flags:
- `--mount --uts --ipc --pid --net` create fresh namespaces for mounts, hostname, IPC, PID tree, and networking.
- `--user --map-root-user` remap your user inside the namespace to appear as root (user namespaces).
- `--fork` spawns a child process inside the new namespaces so your current shell stays intact.

You now have a shell acting like a lightweight container. Validate isolation:
```bash
# Hostname differs from host
hostname container-lab
hostname

# See that PID 1 is your shell in the namespace
ps -ef

# Network namespace is empty (no interfaces besides lo)
ip addr
```

Exit any time with `exit` or `Ctrl+D`.

### 3. Add a Minimal Root Filesystem (Optional)
To get closer to a real container, bind-mount a directory and `chroot` into it.
```bash
sudo mkdir -p /tmp/container-root/{proc,sys,dev}
sudo debootstrap --variant=minbase stable /tmp/container-root http://deb.debian.org/debian

sudo unshare --mount --uts --ipc --pid --net --fork --user --map-root-user bash
mount --make-rprivate /
mount -t proc proc /tmp/container-root/proc
mount --rbind /sys /tmp/container-root/sys
mount --rbind /dev /tmp/container-root/dev
chroot /tmp/container-root /bin/bash
```

Inside the chroot you have a Debian rootfs with its own `/etc`, `/bin`, etc.

### 4. Apply Resource Limits via cgroups v2
While still inside an unshared shell (not necessarily chrooted), create a cgroup and limit CPU/memory:
```bash
CGROUP=/sys/fs/cgroup/container-lab
sudo mkdir -p $CGROUP
echo $$ | sudo tee $CGROUP/cgroup.procs
echo 200000 | sudo tee $CGROUP/cpu.max        # limit to 20% of one CPU (0.2s quota / 1s period)
echo 134217728 | sudo tee $CGROUP/memory.max  # 128 MiB
```

Start a workload (e.g., `stress-ng`, `dd`, or a busy loop) and observe that it stays within the limits.

Clean up:
```bash
sudo rmdir $CGROUP
sudo umount /tmp/container-root/{proc,sys,dev}
sudo rm -rf /tmp/container-root
```

### 5. Reflect
- Containers are just processes with specific kernel features applied.
- Docker/Kubernetes automate these steps, but understanding them helps debug low-level issues.
- Practice with `nsenter` to join existing namespaces and inspect running containers.
