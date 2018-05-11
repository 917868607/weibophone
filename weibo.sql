/*
 Navicat Premium Data Transfer

 Source Server         : 腾讯云
 Source Server Type    : MySQL
 Source Server Version : 100213
 Source Host           :
 Source Schema         : weibo

 Target Server Type    : MySQL
 Target Server Version : 100213
 File Encoding         : 65001

 Date: 12/05/2018 00:04:38
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for commit
-- ----------------------------
DROP TABLE IF EXISTS `commit`;
CREATE TABLE `commit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_id` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `text` text COLLATE utf8mb4_bin NOT NULL COMMENT '回复内容',
  `like_counts` int(40) NOT NULL COMMENT '回复点赞数',
  PRIMARY KEY (`id`),
  KEY `status_id` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=312790 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Table structure for mblog
-- ----------------------------
DROP TABLE IF EXISTS `mblog`;
CREATE TABLE `mblog` (
  `status_id` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '博文ID',
  `uid` bigint(20) NOT NULL COMMENT '用户ID',
  `created_at` datetime NOT NULL COMMENT '发布时间',
  `mblogid` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT '访问博文的地址ID',
  `text` text COLLATE utf8mb4_bin NOT NULL COMMENT '博文内容',
  `reposts_count` bigint(40) NOT NULL COMMENT '转发数',
  `comments_count` bigint(40) NOT NULL COMMENT '评论数',
  `attitudes_count` bigint(40) NOT NULL COMMENT '点赞数',
  PRIMARY KEY (`status_id`) USING BTREE,
  KEY `status_id` (`status_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uid` bigint(20) NOT NULL,
  `name` char(50) COLLATE utf8mb4_bin NOT NULL,
  `gender` char(10) COLLATE utf8mb4_bin NOT NULL,
  `location` char(10) COLLATE utf8mb4_bin NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `friends_count` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `followers_count` int(50) NOT NULL,
  `statuses_count` int(50) NOT NULL,
  `friends` text COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Table structure for wanglihong
-- ----------------------------
DROP TABLE IF EXISTS `wanglihong`;
CREATE TABLE `wanglihong` (
  `status_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '博文ID',
  `uid` bigint(20) NOT NULL COMMENT '用户ID',
  `created_at` datetime NOT NULL COMMENT '发布时间',
  `mblogid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '访问博文的地址ID',
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '博文内容',
  `reposts_count` bigint(40) NOT NULL COMMENT '转发数',
  `comments_count` bigint(40) NOT NULL COMMENT '评论数',
  `attitudes_count` bigint(40) NOT NULL COMMENT '点赞数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
