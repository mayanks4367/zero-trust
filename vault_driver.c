#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/mutex.h>
#include <linux/device.h>
#include <linux/ioctl.h>  // Added for ioctl
#include <linux/timer.h>  // Added for auto-lock timer
#include <linux/jiffies.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("MAYANK");
MODULE_DESCRIPTION("Zero-Trust Secret Vault with Auto-Lock");
MODULE_VERSION("0.2");

#define DEVICE_NAME "secret_vault"
#define CLASS_NAME  "secret_vault_class"
#define MAX_SECRET  4096

// --- IOCTL Definitions ---
// Define a "Magic Number" 'v' and command 1
#define VAULT_MAGIC 'v'
#define IOCTL_UNLOCK_VAULT _IOW(VAULT_MAGIC, 1, int)
#define VAULT_PIN 1337  // The secret PIN to unlock

static char secret_buf[MAX_SECRET];
static size_t secret_len = 0;
static DEFINE_MUTEX(secret_mutex);

// Locking Mechanism
static int is_unlocked = 0; // 0 = Locked (Default), 1 = Unlocked
static struct timer_list lock_timer; // Timer for auto-locking

static dev_t device_num;
static struct cdev secret_cdev;
static struct class *secret_class;
static struct device *secret_device;

// --- Timer Callback ---
// This function runs automatically after 30 seconds
static void auto_lock_callback(struct timer_list *t)
{
    mutex_lock(&secret_mutex);
    is_unlocked = 0;
    mutex_unlock(&secret_mutex);
    pr_info("[Vault]: Timeout reached. Vault AUTO-LOCKED.\n");
}

static int my_open(struct inode *inode, struct file *file)
{
    return 0;
}

static int my_close(struct inode *inode, struct file *file)
{
    return 0;
}

static ssize_t my_read(struct file *file, char __user *buf, size_t count, loff_t *ppos)
{
    size_t to_copy;
    int ret;

    if (mutex_lock_interruptible(&secret_mutex))
        return -ERESTARTSYS;

    // --- SECURITY CHECK ---
    if (is_unlocked == 0) {
        mutex_unlock(&secret_mutex);
        pr_warn("[Vault]: Unauthorized Read Attempt!\n");
        return -EACCES; // Permission Denied
    }

    if (*ppos >= secret_len) {
        mutex_unlock(&secret_mutex);
        return 0;  // EOF
    }

    to_copy = min(count, secret_len - *ppos);

    ret = copy_to_user(buf, secret_buf + *ppos, to_copy);
    if (ret) {
        mutex_unlock(&secret_mutex);
        return -EFAULT;
    }

    *ppos += to_copy;
    mutex_unlock(&secret_mutex);
    return to_copy;
}

static ssize_t my_write(struct file *file, const char __user *buf, size_t count, loff_t *ppos)
{
    size_t to_copy;
    int ret;

    if (mutex_lock_interruptible(&secret_mutex))
        return -ERESTARTSYS;

    // --- SECURITY CHECK ---
    if (is_unlocked == 0) {
        mutex_unlock(&secret_mutex);
        pr_warn("[Vault]: Unauthorized Write Attempt!\n");
        return -EACCES; // Permission Denied
    }

    to_copy = min(count, (size_t)MAX_SECRET);

    ret = copy_from_user(secret_buf, buf, to_copy);
    if (ret) {
        mutex_unlock(&secret_mutex);
        return -EFAULT;
    }

    secret_len = to_copy;
    *ppos = 0;
    mutex_unlock(&secret_mutex);
    return to_copy;
}

// --- IOCTL Handler (The Keyhole) ---
static long my_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    int user_pin;
    
    switch(cmd) {
        case IOCTL_UNLOCK_VAULT:
            if (copy_from_user(&user_pin, (int32_t *)arg, sizeof(user_pin))) {
                return -EFAULT;
            }

            if (user_pin == VAULT_PIN) {
                mutex_lock(&secret_mutex);
                is_unlocked = 1;
                // Set timer to auto-lock in 30 seconds (30 * HZ)
                mod_timer(&lock_timer, jiffies + msecs_to_jiffies(30000));
                mutex_unlock(&secret_mutex);
                pr_info("[Vault]: PIN Accepted. Vault UNLOCKED for 30s.\n");
                return 0; // Success
            } else {
                pr_err("[Vault]: Invalid PIN!\n");
                return -EACCES; // Access Denied
            }
            break;
        default:
            return -EINVAL;
    }
    return 0;
}

static struct file_operations fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_close,
    .read    = my_read,
    .write   = my_write,
    .unlocked_ioctl = my_ioctl, // Hook up the IOCTL
};

static int __init secret_init(void)
{
    int ret;

    // Initialize Timer
    timer_setup(&lock_timer, auto_lock_callback, 0);

    // 1. Allocate major/minor
    ret = alloc_chrdev_region(&device_num, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        pr_err("alloc_chrdev_region failed\n");
        return ret;
    }

    // 2. Initialize cdev
    cdev_init(&secret_cdev, &fops);
    secret_cdev.owner = THIS_MODULE;

    // 3. Add cdev
    ret = cdev_add(&secret_cdev, device_num, 1);
    if (ret < 0) {
        pr_err("cdev_add failed\n");
        goto err_chrdev;
    }

    // 4. Create class
    secret_class = class_create(CLASS_NAME);
    if (IS_ERR(secret_class)) {
        ret = PTR_ERR(secret_class);
        pr_err("class_create failed\n");
        goto err_cdev;
    }

    // 5. Create device node
    secret_device = device_create(secret_class, NULL, device_num, NULL, DEVICE_NAME);
    if (IS_ERR(secret_device)) {
        ret = PTR_ERR(secret_device);
        pr_err("device_create failed\n");
        goto err_class;
    }

    mutex_init(&secret_mutex);
    pr_info("Zero-Trust Vault registered. State: LOCKED\n");
    return 0;

err_class:
    class_destroy(secret_class);
err_cdev:
    cdev_del(&secret_cdev);
err_chrdev:
    unregister_chrdev_region(device_num, 1);
    return ret;
}

static void __exit secret_exit(void)
{
    timer_delete_sync(&lock_timer); // Stop timer so it doesn't crash after unload
    device_destroy(secret_class, device_num);
    class_destroy(secret_class);
    cdev_del(&secret_cdev);
    unregister_chrdev_region(device_num, 1);
    pr_info("Secret Vault unregistered\n");
}

module_init(secret_init);
module_exit(secret_exit);
