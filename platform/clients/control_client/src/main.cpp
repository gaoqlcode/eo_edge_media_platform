/**
 * @file main.cpp
 * @brief control_client — Qt 简易地面站（对照 eo_pod_gcs）
 * 内容：启动时 HTTP 拉 BFF dashboard，窗口展示文本摘要
 */
#include <QApplication>
#include <QLabel>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QVBoxLayout>
#include <QWidget>
#include <QUrl>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);  // Qt 应用对象
    QWidget window;  // 主窗口
    window.setWindowTitle(QString::fromUtf8("EMP Control Client"));
    auto* layout = new QVBoxLayout(&window);  // 垂直布局
    auto* label = new QLabel(QString::fromUtf8("正在请求 BFF /api/bff/dashboard ..."));
    label->setWordWrap(true);
    layout->addWidget(label);

    QNetworkAccessManager nam;  // 网络管理器
    QNetworkRequest req(QUrl("http://127.0.0.1:8105/api/bff/dashboard"));
    QNetworkReply* reply = nam.get(req);  // 异步 GET
    QObject::connect(reply, &QNetworkReply::finished, [&]() {
        if (reply->error() != QNetworkReply::NoError) {
            label->setText(QString::fromUtf8("请求失败: ") + reply->errorString() +
                           QString::fromUtf8("\n请先启动 control_bff(8105) 等服务"));
        } else {
            label->setText(QString::fromUtf8(reply->readAll()));
        }
        reply->deleteLater();
    });

    window.resize(640, 480);
    window.show();
    return app.exec();
}
