# Heap-Based Cryptography

## Description

> Tu aimes la hash-based crypto ? Tant mieux.

Avec uniquement un accès via socket TCP au challenge, l'objectif est de satisfaire la fonction *claim_flag* afin de déclencher le *print(FLAG)*.

## Déploiement

```bash
git submodule update --init --recursive
cd deploy
docker compose up --build
```

## Accès

```bash
nc 127.0.0.1 1234
```

