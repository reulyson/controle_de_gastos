"""Agregador de rotas /api/v1."""

from fastapi import APIRouter

from app.modulos.cartoes.rotas import roteador as roteador_cartoes
from app.modulos.carteiras.rotas import roteador as roteador_carteiras
from app.modulos.categorias.rotas import roteador as roteador_categorias
from app.modulos.compras.rotas import roteador as roteador_compras
from app.modulos.configuracoes.rotas import roteador as roteador_configuracoes
from app.modulos.controle.rotas import roteador as roteador_controle
from app.modulos.despesas.rotas import roteador as roteador_despesas
from app.modulos.fechamento.rotas import roteador as roteador_fechamento
from app.modulos.mensais.rotas import roteador_despesas as roteador_despesas_mensais
from app.modulos.mensais.rotas import roteador_receitas as roteador_receitas_mensais
from app.modulos.pagamentos.rotas import roteador as roteador_pagamentos
from app.modulos.receitas.rotas import roteador as roteador_receitas
from app.modulos.tags.rotas import roteador as roteador_tags

roteador_v1 = APIRouter(prefix="/api/v1")

roteador_v1.include_router(roteador_carteiras)
roteador_v1.include_router(roteador_categorias)
roteador_v1.include_router(roteador_tags)
roteador_v1.include_router(roteador_receitas)
roteador_v1.include_router(roteador_receitas_mensais)
roteador_v1.include_router(roteador_despesas)
roteador_v1.include_router(roteador_despesas_mensais)
roteador_v1.include_router(roteador_cartoes)
roteador_v1.include_router(roteador_compras)
roteador_v1.include_router(roteador_pagamentos)
roteador_v1.include_router(roteador_controle)
roteador_v1.include_router(roteador_fechamento)
roteador_v1.include_router(roteador_configuracoes)
