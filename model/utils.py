import os
from collections import OrderedDict

import torch
import torch.nn as nn
from torch.optim import lr_scheduler

from .loss import MixMatchLoss, SCELoss, SimCLRLoss
from .network import resnet_cifar


def get_network(network_config):
    if "resnet18_cifar" in network_config:
        model = resnet_cifar.resnet18(**network_config["resnet18_cifar"])
    else:
        raise ValueError("Network {} is not supported.".format(network_config))

    return model


def get_criterion(criterion_config):
    if "cross_entropy" in criterion_config:
        criterion = nn.CrossEntropyLoss(**criterion_config["cross_entropy"])
    elif "simclr" in criterion_config:
        criterion = SimCLRLoss(**criterion_config["simclr"])
    elif "sce" in criterion_config:
        criterion = SCELoss(**criterion_config["sce"])
    elif "mixmatch" in criterion_config:
        criterion = MixMatchLoss(**criterion_config["mixmatch"])
    else:
        raise ValueError(
            "Criterion {} is not supported.".format(criterion_config)
        )

    return criterion


def get_optimizer(model, optimizer_config):
    if "Adam" in optimizer_config:
        optimizer = torch.optim.Adam(model.parameters(), **optimizer_config["Adam"])
    elif "SGD" in optimizer_config:
        optimizer = torch.optim.SGD(model.parameters(), **optimizer_config["SGD"])
    else:
        raise NotImplementedError(
            "Optimizer {} is not supported.".format(optimizer_config)
        )

    return optimizer


def get_scheduler(optimizer, lr_scheduler_config):
    if lr_scheduler_config is None:
        scheduler = None
    elif "multi_step" in lr_scheduler_config:
        scheduler = lr_scheduler.MultiStepLR(
            optimizer, **lr_scheduler_config["multi_step"]
        )
    elif "cosine_annealing" in lr_scheduler_config:
        scheduler = lr_scheduler.CosineAnnealingLR(
            optimizer, **lr_scheduler_config["cosine_annealing"]
        )
    else:
        raise ValueError(
            "Learning rate scheduler {} is not supported.".format(lr_scheduler_config)
        )

    return scheduler


def load_state(
    model, resume, ckpt_dir, gpu, logger, optimizer=None, scheduler=None, is_best=False
):
    """Load training state from checkpoint.

    Args:
        model (torch.nn.Module): Model to resume.
        resume (string): Checkpoint name (empty string means the latest checkpoint)
            or False (means training from scratch).
        ckpt_dir (string): Checkpoint directory.
        gpu (string or int): The specified single gpu to load checkpoint.
        logger (logging.logger): The logger.
        optimizer (torch.optim.Optimizer): Optimizer to resume (default: None).
        scheduler (torch.optim._LRScheduler): Learning rate scheduler to
            resume (default: None).
        is_best (boolean, optional): Set True to load checkpoint
            with `best_acc` (default: False).

    Returns:
        resumed_epoch: The epoch to resume (0 means training from scratch.)
        best_acc: The best test accuracy in the training.
        best_epoch: The epoch getting the `best_acc`.
    """
    if resume == "False":
        logger.warning("Training from scratch.")
        resumed_epoch = 0
        if is_best:
            best_acc = 0
            best_epoch = 0
            return resumed_epoch, best_acc, best_epoch
        else:
            return resumed_epoch
    else:
        # Load checkpoint.
        if resume == "":
            ckpt_path = os.path.join(ckpt_dir, "latest_model.pt")
        else:
            ckpt_path = os.path.join(ckpt_dir, resume)
        ckpt = torch.load(ckpt_path, map_location="cuda:{}".format(gpu))
        logger.info("Load training state from the checkpoint {}:".format(ckpt_path))
        logger.info("Epoch: {}, result: {}".format(ckpt["epoch"], ckpt["result"]))
        if "parallel" in str(type(model)):
            # DataParallel or DistributedParallel.
            model.load_state_dict(ckpt["model_state_dict"])
        else:
            # Remove "module." in `model_state_dict` if saved
            # from DDP wrapped model in the single GPU training.
            model_state_dict = OrderedDict()
            for k, v in ckpt["model_state_dict"].items():
                if k.startswith("module."):
                    k = k.replace("module.", "")
                    model_state_dict[k] = v
                else:
                    model_state_dict[k] = v
            model.load_state_dict(model_state_dict)
        resumed_epoch = ckpt["epoch"]
        if optimizer is not None:
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        if scheduler is not None:
            scheduler.load_state_dict(ckpt["scheduler_state_dict"])
        if is_best:
            best_acc = ckpt["best_acc"]
            best_epoch = ckpt["best_epoch"]
            return resumed_epoch, best_acc, best_epoch
        else:
            return resumed_epoch


def get_saved_epoch(
    num_epochs, num_stage_epochs=100, min_interval=20, max_interval=100
):
    if num_epochs >= num_stage_epochs:
        early = set(range(min_interval, num_stage_epochs, min_interval))
        mid = set(range(num_stage_epochs, num_epochs - num_stage_epochs, max_interval))
        later = set(
            range(
                num_epochs - num_stage_epochs, num_epochs + min_interval, min_interval
            )
        )
        if num_epochs == num_stage_epochs:
            later.remove(0)
        saved_epoch = early.union(mid).union(later)
    else:
        raise ValueError(
            "The num_epochs: {} must be equal or greater than num_stage_epochs: {}".format(
                num_epochs, num_stage_epochs
            )
        )

    return saved_epoch
