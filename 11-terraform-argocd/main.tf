provider "helm" {
  kubernetes = {
    config_path = pathexpand("~/.kube/config.k3d")
  }
}

resource "helm_release" "argocd" {
  name             = "argocd"
  namespace        = "argocd"
  create_namespace = true

  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "9.3.4"

  values = [file("${path.module}/values/argocd.yaml")]
}

resource "helm_release" "argo_rollouts" {
  name             = "argo-rollouts"
  namespace        = "argo-rollouts"
  create_namespace = true
  depends_on       = [helm_release.argocd]

  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-rollouts"
  version    = "2.40.5"

  values = [file("${path.module}/values/rollouts.yaml")]
}
