CREATE DATABASE IF NOT EXISTS tutoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 科目字典表（供前端下拉选择）
CREATE TABLE IF NOT EXISTS subjects (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE COMMENT '科目名称',
  parent_id INT UNSIGNED DEFAULT NULL COMMENT '父科目ID（如"理科"包含"数学","物理"）',
  sort_order INT DEFAULT 0,
  INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO subjects (name, parent_id, sort_order) VALUES
('语文', NULL, 1), ('数学', NULL, 2), ('英语', NULL, 3),
('物理', NULL, 4), ('化学', NULL, 5), ('生物', NULL, 6),
('政治', NULL, 7), ('历史', NULL, 8), ('地理', NULL, 9),
('科学', NULL, 10), ('编程', NULL, 11), ('美术', NULL, 12),
('音乐', NULL, 13), ('体育', NULL, 14);
