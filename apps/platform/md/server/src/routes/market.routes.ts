import { Router } from 'express';
import * as marketController from '../controllers/market.controller';

const router = Router();

/**
 * @route   GET /api/v1/market/vendors
 * @desc    获取供应商列表
 * @access  Public
 */
router.get('/vendors', marketController.getMarketVendors);

/**
 * @route   GET /api/v1/market/vendors/:username
 * @desc    获取供应商详情
 * @access  Public
 */
router.get('/vendors/:username', marketController.getVendorProfile);

/**
 * @route   GET /api/v1/market/stats
 * @desc    获取市场统计数据
 * @access  Public
 */
router.get('/stats', marketController.getMarketStats);

/**
 * @route   GET /api/v1/market/products
 * @desc    搜索产品
 * @access  Public
 */
router.get('/products', marketController.searchProducts);

/**
 * @route   GET /api/v1/market/products/:id
 * @desc    获取产品详情
 * @access  Public
 */
router.get('/products/:id', marketController.getProductDetail);

export default router;
