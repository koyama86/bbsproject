from django.shortcuts import render
from django.views import generic # 汎用ビューのインポート
from django.urls import reverse_lazy # reverse_lazy関数のインポート
from django.contrib.auth.mixins import LoginRequiredMixin   
from django.core.exceptions import PermissionDenied
from .models import Article
from .forms import SearchForm
 #modelsのやつ
# Create your views here.

#indexViewkurasu tukuruyo
class IndexView(generic.ListView):
    model = Article #used Article model 
    template_name = ('bbs/index.html') #used template


class DetailView(generic.DetailView):
    model = Article
    template_name = ('bbs/detail.html')

# 新規投稿はログイン中のみ
class CreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Article
    template_name = 'bbs/create.html'
    fields = '__all__'
    fields = ['content']

    # 格納する値をチェック
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CreateView,self).form_valid(form)

class UpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Article
    template_name = 'bbs/create.html'
    fields = ['content'] #項目をcontentの中に変更

    "dispatchメソッドで権限チェックを追加"
    def dispatch(self, request, *args, **kwargs):
        # 編集対象の投稿オブジェクトを取得
        obj = self.get_object()
        # 投稿者と現在のユーザーが一致しない場合は403エラーを出力
        if obj.author != self.request.user:
            raise PermissionDenied('編集権限がありません')
        # 親クラスのdispatchを呼び出して通常の処理を継続 
        return super(UpdateView,self).dispatch(request, *args, **kwargs)

class DeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Article
    template_name = 'bbs/delete.html'
    success_url = reverse_lazy('bbs:index')

    def dispatch(self, request, *args, **kwargs):
        # 比較対処の投稿オブジェクトを取得
        obj = self.get_object()
        if obj.author != self.request.user:
            raise PermissionDenied('削除権限がありません') 
        return super(DeleteView,self).dispatch(request, *args, **kwargs)

def search(request):
    articles = None
    seachform = SearchForm(request.GET)

    #formに正常なデータがあれば
    if seachform.is_valid():
        query = seachform.cleaned_data['words'] #queryにフォームが持っているデータを代入
        articles = Article.objects.filter(content__icontains=query) #クエリを含むレコードをfilterメソッドで呼び出し

        return render(request,'bbs/results.html',{'articles':articles,'searchform':seachform})
    

def custom_permission_denied_view(request,exception):
    return render(request,'403.html',{'error_message' : str(exception)},status=403)